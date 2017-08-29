#!/bin/sh

dir=${1:-.}

# the idea is the following; we count the number of "parts" (parent dirs) the
# requested dir has...
parts=0
IFS=/; for _ in $dir; do
    parts=$(( parts + 1 ))
done; unset IFS

posix_find() {
    # ...and use cut with a delimiter of / to only print the field that is after
    # the requested dir; in other words, we only keep the name of the immediate
    # subdirectory that is currently being processed
    find "$1"                       \
        | cut -d/ -f$((parts + 1))  \
        | sort                      \
        | uniq -c                   \
        | sort -bn
}

posix_find2() {
    # Compared to the previous this will "condense" all the files in the base
    # dir into a single '.' group, like gnu_find() does.
    for f in "$1/"* "$1/".[!.]*; do
        if [ ! -e "$f" ]; then
            continue
        elif [ -d "$f" ]; then
            find "$f"
        else
            echo .
        fi
    done                    \
        | cut -d/ -f$parts  \
        | sort              \
        | uniq -c           \
        | sort -bn
}

posix_find3() {
    # I could potentially replace 'cut' in the above solution with 'sed',
    #     find "$1" | sed -e '/$escaped_dir/ s/^$escaped_dir//'
    # The only problem is how to escape the directory for use in a regex.  See
    #     https://stackoverflow.com/q/29613304
    true
}

gnu_find() {
    is_subdir="*/*"
    for _ in $(seq $parts); do
        is_subdir="$is_subdir/*"
    done

    find "$1" -path "$is_subdir" -printf '%P\0' -o -type f -printf '.\0' \
        | cut  -z -d/ -f1                                                   \
        | sort -z                                                           \
        | uniq -zc                                                          \
        | sort -zbn                                                         \
        | xargs -0 printf '%s\n'
}

gnu_find "$dir"
