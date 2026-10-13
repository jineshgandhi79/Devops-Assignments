# Stage 1: Build the application
FROM golang:1.20-alpine AS builder

WORKDIR /app
COPY main.go .
RUN go build -o server main.go

# Stage 2: Create a minimal production image
FROM alpine:latest

WORKDIR /root/
COPY --from=builder /app/server .
EXPOSE 8080

CMD ["./server"]
