package main

import (
	"fmt"
	"net/http"
	"os"
)

// Função que será substituída nos testes
var serverListenAndServe = http.ListenAndServe

func main() {
	run()
}

// Função principal para rodar o servidor
func run() {
	port := getPort()
	fmt.Printf("Listening on port %s\n", port)
	startServer(port)
}

func startServer(port string) {
	http.HandleFunc("/status", statusHandler)
	// Substituímos http.ListenAndServe por uma variável que pode ser mockada nos testes
	serverListenAndServe(fmt.Sprintf(":%s", port), nil)
}

func statusHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("UP"))
}

func getPort() string {
	port := os.Getenv("PORT")
	if port == "" {
		return "8080"
	}
	return port
}
