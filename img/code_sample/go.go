package main

import (
    "fmt"
    "time"
)

func main() {
    queue := make(chan int, 1)
    go func() {
        for {
            data := <- queue
            fmt.Print(data, " ")
        }
    }()

    for i := 0; i < 10; i ++ {
        queue <- i
    }
    time.Sleep(time.Second)
}