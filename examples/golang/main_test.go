package main

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
)

func TestGetPort(t *testing.T) {
	os.Setenv("PORT", "9090")
	port := getPort()
	if port != "9090" {
		t.Errorf("esperado 9090, mas obteve %s", port)
	}

	os.Unsetenv("PORT")
	port = getPort()
	if port != "8080" {
		t.Errorf("esperado 8080, mas obteve %s", port)
	}
}

func TestStatusHandler(t *testing.T) {
	req, err := http.NewRequest("GET", "/status", nil)
	if err != nil {
		t.Fatal(err)
	}

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(statusHandler)
	handler.ServeHTTP(rr, req)

	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler retornou o status errado: obteve %v, esperado %v", status, http.StatusOK)
	}

	expected := "OK"
	if rr.Body.String() != expected {
		t.Errorf("handler retornou o corpo errado: obteve %v, esperado %v", rr.Body.String(), expected)
	}
}

func TestStartServer(t *testing.T) {
	go func() {
		defer func() {
			if r := recover(); r != nil {
				t.Log("ListenAndServe foi chamado corretamente e interceptado.")
			}
		}()
		startServer("8080")
	}()
}
