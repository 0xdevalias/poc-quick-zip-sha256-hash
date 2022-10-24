# poc-quick-zip-sha256-hash

Calculate the SHA256 hash over a Zip file's 'Central Directory' record (which contains the list of files + their CRC32 checksums)

## Concept

This concept was originally described on a [PR](https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/2459#issuecomment-1288307764) <sup>(ref: [1](https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/2459#issuecomment-1277933676), [2](https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/2459#issuecomment-1278782886))</sup> on [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

> [@dfaker](https://github.com/dfaker): [@raefu](https://github.com/raefu) had a nice and consistently fast solution to this: hashing the zip directory section at the end of the file so it's a hash of the attributes and crcs of all the contents.
>
> [@dfaker](https://github.com/dfaker): it's a small section at the end of the file, starting with the signature `0x02014b50`, taking the last MB of the .pt sould capture it.

## Implementation Overview

- Open the zip file (`model.ckpt`) in binary read mode
- Seek to 22 bytes from the end of the file (the length of the 'end of central directory' (EOCD) record so long as it has no comments in it
- Read in the EOCD record, extract various parts of it (including the 'central directory' (CD) record offset + length), and do some rudimentrary error checking
- Seek to the CD record offset
- Read in CD record length bytes, extract the CD signature, do some rudimentary error checking
- Calculate the SHA256 hash of the CD record bytes
- Display the hash + write it to `model.sha256-cd`

## References

### Zip File Format

- https://en.wikipedia.org/wiki/ZIP_(file_format)#File_headers
  - > All multi-byte values in the header are stored in little-endian byte order.
  - > All length fields count the length in bytes.
  - https://en.wikipedia.org/wiki/ZIP_(file_format)#End_of_central_directory_record_(EOCD)
  - https://en.wikipedia.org/wiki/ZIP_(file_format)#Central_directory_file_header
- https://en.wikipedia.org/wiki/ZIP_(file_format)#ZIP64
