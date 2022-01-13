package main

import (
	"compress/gzip"
	"crypto/tls"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
)

var (
	fa      = flag.String("front", ":443", "listening address")
	ba      = flag.String("back", "localhost:8080", "forwarding to backend address")
	public  = flag.String("cert", "cert.pem", "SSL certificate location")
	private = flag.String("key", "key.pem", "SSL key location")
	verbose = flag.Bool("verbose", false, "Verbose output")
)

type GzipWriter struct {
	io.Writer
	http.ResponseWriter
}

func (w GzipWriter) WriteHeader(status int) {
	w.Header().Del("Content-Length")
	w.ResponseWriter.WriteHeader(status)
}

func (w GzipWriter) Write(b []byte) (int, error) {
	return w.Writer.Write(b)
}

func main() {
	flag.Parse()

	url := url.URL{
		Scheme: "http",
		Host:   *ba,
	}
	proxy := httputil.NewSingleHostReverseProxy(&url)

	director := proxy.Director
	proxy.Director = func(req *http.Request) {
		director(req)
		req.Host = req.URL.Host
	}

	log.Println("Listening on", *fa)

	config := tls.Config{
		CipherSuites: []uint16{
			tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
			tls.TLS_ECDHE_ECDSA_WITH_RC4_128_SHA,
			tls.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
			tls.TLS_RSA_WITH_AES_128_CBC_SHA,
			tls.TLS_RSA_WITH_AES_256_CBC_SHA,
			tls.TLS_RSA_WITH_AES_128_CBC_SHA256,
			tls.TLS_RSA_WITH_AES_128_GCM_SHA256,
			tls.TLS_RSA_WITH_AES_256_GCM_SHA384,
		},
		PreferServerCipherSuites: true,
		InsecureSkipVerify:       true,
		MinVersion:               tls.VersionTLS11,
		MaxVersion:               tls.VersionTLS13,
	}

	s := http.Server{
		Addr:      *fa,
		TLSConfig: &config,
	}
	s.Handler = Forward(proxy)
	err := s.ListenAndServeTLS(*public, *private)
	log.Fatalln(err)
}

func Forward(handler http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if clientIP, _, err := net.SplitHostPort(r.RemoteAddr); err == nil {
			r.Header.Set("X-Forwarded-For", clientIP)
		}

		if verbose != nil && *verbose {
			b, err := httputil.DumpRequest(r, true)

			if err != nil {
				fmt.Println("Error " + err.Error())
			} else {
				fmt.Println(string(b))
			}
		}

		w.Header().Set("X-Forwarded-Host", r.Host)
		w.Header().Set("X-Forwarded-Proto", "https")

		ce := r.Header.Get("Accept-Encoding")
		if ce != "" && ce == "gzip" {
			gz := gzip.NewWriter(w)
			defer gz.Close()

			w.Header().Set("Content-Encoding", "gzip")

			g := GzipWriter{Writer: gz, ResponseWriter: w}
			handler.ServeHTTP(g, r)
		} else {
			handler.ServeHTTP(w, r)
		}
	})
}
