package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello World from Docker multi-stage build\n")
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("Server is running on port 8080...")
	http.ListenAndServe(":8080", nil)
}
