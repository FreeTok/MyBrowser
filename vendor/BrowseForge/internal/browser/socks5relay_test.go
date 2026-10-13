package browser

import (
	"errors"
	"io"
	"net"
	"testing"
	"time"
)

type recordingProxyDialer struct{ destination chan string }

func (d recordingProxyDialer) Dial(network, address string) (net.Conn, error) {
	d.destination <- address
	return nil, errors.New("test stops before upstream connection")
}

func TestSOCKS5RelayDestinationParsing(t *testing.T) {
	for _, tt := range []struct {
		name    string
		kind    byte
		address []byte
		want    string
	}{
		{"hostname", 3, []byte("audit.invalid"), "audit.invalid:19283"},
		{"IPv6 sent as domain by Firefox", 3, []byte("2001:db8::123"), "[2001:db8::123]:19283"},
		{"IPv6 address", 4, net.ParseIP("2001:db8::123").To16(), "[2001:db8::123]:19283"},
		{"IPv4 address", 1, net.ParseIP("192.0.2.123").To4(), "192.0.2.123:19283"},
	} {
		t.Run(tt.name, func(t *testing.T) {
			server, client := net.Pipe()
			defer client.Close()
			client.SetDeadline(time.Now().Add(3 * time.Second))
			destinations := make(chan string, 1)
			relay := SOCKS5Relay{dialer: recordingProxyDialer{destinations}}
			done := make(chan struct{})
			go func() { relay.handle(server); close(done) }()
			if _, err := client.Write([]byte{5, 1, 0}); err != nil {
				t.Fatal(err)
			}
			greeting := make([]byte, 2)
			if _, err := io.ReadFull(client, greeting); err != nil {
				t.Fatal(err)
			}
			request := []byte{5, 1, 0, tt.kind}
			if tt.kind == 3 {
				request = append(request, byte(len(tt.address)))
			}
			request = append(request, tt.address...)
			request = append(request, 0x4b, 0x53)
			if _, err := client.Write(request); err != nil {
				t.Fatal(err)
			}
			reply := make([]byte, 10)
			if _, err := io.ReadFull(client, reply); err != nil {
				t.Fatal(err)
			}
			if got := <-destinations; got != tt.want {
				t.Fatalf("upstream destination = %q, want %q", got, tt.want)
			}
			<-done
		})
	}
}
