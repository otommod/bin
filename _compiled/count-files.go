package main

// Worth checking out is also fastwalk.go and its simblings in
//     https://github.com/golang/tools/
// Unfortunately, it's not possible to import it :(

import (
	"fmt"
	"github.com/MichaelTJones/walk"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type kv struct {
	key   string
	value int
}

func countingWalker(basedir string, increment chan string) walk.WalkFunc {
	return func(path string, info os.FileInfo, err error) error {
		// if info.IsDir() {
		//     return nil
		// }

		subdirName, err := filepath.Rel(basedir, path)
		if err != nil {
			return err
		}
		if i := strings.IndexRune(subdirName, os.PathSeparator); i < 0 {
			// subdirName contains no slashes, so it's a direct child of basedir itself
			subdirName = "."
		} else {
			subdirName = subdirName[:i]
		}

		increment <- subdirName
		return nil
	}
}

func main() {
	basedir := "."
	if len(os.Args) > 1 {
		basedir = os.Args[1]
	}

	counts := make(map[string]int)
	ch := make(chan string)
	done := make(chan bool)
	go func() {
		for dir := range ch {
			counts[dir] += 1
		}
		done <- true
	}()

	err := walk.Walk(basedir, countingWalker(basedir, ch))
	if err != nil {
		panic(err)
	}
	close(ch)
	<-done

	// '.' counts itself as well and that's no good
	counts["."] -= 1

	sorted := make([]kv, 0, len(counts))
	for k, v := range counts {
		sorted = append(sorted, kv{k, v})
	}
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].value < sorted[j].value
	})

	// we can be sure that sorted contains at least '.'
	maxLen := len(fmt.Sprintf("%d", sorted[len(sorted)-1].value))
	for _, pair := range sorted {
		fmt.Printf(" %*d %s\n", maxLen, pair.value, pair.key)
	}
}
