package main

import (
	"bufio"
	"encoding/binary"
	"flag"
	"fmt"
	"image"
	"image/png"
	"io"
	"os"
	"strconv"
)

type Uint32Scanner struct {
	*bufio.Scanner
}

func NewUint32Scanner(r io.Reader) *Uint32Scanner {
	s := &Uint32Scanner{
		bufio.NewScanner(r),
	}
	s.Split(s.splitter)
	return s
}

func (s *Uint32Scanner) splitter(data []byte, atEOF bool) (int, []byte, error) {
	var inNumber bool
	var start int
	for i, c := range data {
		switch {
		case '0' <= c && c <= '9' && inNumber: // do nothing
		case '0' <= c && c <= '9' && !inNumber:
			start = i
			inNumber = true
		case inNumber:
			token := data[start:i]
			_, err := strconv.ParseUint(string(token), 10, 32)
			return i, token, err
		}
	}
	return 0, nil, nil
}

func (s *Uint32Scanner) Uint32() uint32 {
	// We've already made sure that any token will be a uint32
	i, _ := strconv.ParseUint(s.Text(), 10, 32)
	return uint32(i)
}

func main() {
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: xprop -notype 32c _NET_WM_ICON | %s >file.png\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Extracts the icon of running applications.\n")
		fmt.Fprintf(os.Stderr, "Named after CARDINALs, what X11 calls unsigned ints.\n")
		flag.PrintDefaults()
	}
	flag.Parse()

	scanner := NewUint32Scanner(os.Stdin)

	var width32 uint32
	if !scanner.Scan() {
		if err := scanner.Err(); err != nil {
			panic(err)
		}
		panic("unexpected EOF")
	}
	width32 = scanner.Uint32()

	var height32 uint32
	if !scanner.Scan() {
		if err := scanner.Err(); err != nil {
			panic(err)
		}
		panic("unexpected EOF")
	}
	height32 = scanner.Uint32()

	var argb = make([]byte, 4)
	var imageData []uint8
	for scanner.Scan() {
		num := scanner.Uint32()
		binary.BigEndian.PutUint32(argb, num)

		imageData = append(imageData, argb[1]) /* red */
		imageData = append(imageData, argb[2]) /* green */
		imageData = append(imageData, argb[3]) /* blue */
		imageData = append(imageData, argb[0]) /* alpha */
	}

	if err := scanner.Err(); err != nil {
		panic(err)
	}

	err := png.Encode(os.Stdout, &image.RGBA{
		Pix:    imageData,
		Stride: int(width32) * 4,
		Rect:   image.Rect(0, 0, int(width32), int(height32)),
	})
	if err != nil {
		panic(err)
	}
}
