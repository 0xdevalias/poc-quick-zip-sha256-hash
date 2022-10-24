#!/usr/bin/env python3

import os
import time
import hashlib

# # NOTE: You could also attempt to do this with a higher level library such as ZipFile,
# # though i'm not sure how to get the bytes for the central directory to hash them,
# # by doing that.
#
# from zipfile import ZipFile
# 
# with ZipFile('model.ckpt', 'r') as ckpt:
#   for zipInfo in ckpt.infolist():
#     print(zipInfo)

modelpath = "model.ckpt"
hashpath = "model.sha256-cd"

# https://en.wikipedia.org/wiki/ZIP_(file_format)#Central_directory_file_header
cd_sig = b'PK\x01\x02'

# https://en.wikipedia.org/wiki/ZIP_(file_format)#End_of_central_directory_record_(EOCD)
eocd_sig = b'PK\x05\x06'
eocd_size_without_comments = 22

with open(modelpath, 'rb') as fh:
  # Seek to where we expect the End of Central Directory (EOCD) record to start and read it in
  fh.seek(-eocd_size_without_comments, os.SEEK_END)
  ckpt_eocd = fh.read()

  # https://en.wikipedia.org/wiki/ZIP_(file_format)#End_of_central_directory_record_(EOCD)
  ckpt_eocd_sig = ckpt_eocd[0:4]

  if ckpt_eocd_sig != eocd_sig:
    raise Exception("Didn't find the *.ckpt Zip file End of Central Directory (EOCD) signature where we expected to. Is the *.ckpt corrupted, or does the Zip file have comments in it?")
    # NOTE: If the Zip file has comments, then you'd need to seek further back in chunks, and search for the EOCD signature

  # https://en.wikipedia.org/wiki/ZIP_(file_format)#End_of_central_directory_record_(EOCD)
  ckpt_eocd_cd_size               = ckpt_eocd[0:4]
  ckpt_eocd_this_disk_num         = ckpt_eocd[4:6]
  ckpt_eocd_cd_disk_start         = ckpt_eocd[6:8]
  ckpt_eocd_cd_disk_record_count  = int.from_bytes(ckpt_eocd[8:10], "little")
  ckpt_eocd_cd_total_record_count = int.from_bytes(ckpt_eocd[10:12], "little")
  ckpt_eocd_cd_size_bytes         = int.from_bytes(ckpt_eocd[12:16], "little")
  ckpt_eocd_cd_offset             = int.from_bytes(ckpt_eocd[16:20], "little")

  if ckpt_eocd_this_disk_num != ckpt_eocd_cd_disk_start:
    raise Exception("The *.ckpt Zip file Central Directory (CD) is split over multiple disks, which is an edgecase we don't currently handle")

  # Seek to where we expect the Central Directory (CD) record to start and read it in
  fh.seek(ckpt_eocd_cd_offset, os.SEEK_SET)
  ckpt_cd = fh.read(ckpt_eocd_cd_size_bytes)

  # https://en.wikipedia.org/wiki/ZIP_(file_format)#Central_directory_file_header
  ckpt_cd_sig = ckpt_cd[0:4]

  if ckpt_cd_sig != cd_sig:
    raise Exception("Didn't find the *.ckpt Zip file Central Directory (CD) signature where we expected to. Is the *.ckpt corrupted?")

  # rest_of_file = fh.read()
  # print(len(rest_of_file))
  # print(rest_of_file)
  # https://en.wikipedia.org/wiki/ZIP_(file_format)#ZIP64
  # https://en.wikipedia.org/wiki/ZIP_(file_format)#File_headers
  #   PK\x06\x06 is the ZIP64_CENTRAL_DIRECTORY_END
  #   PK\x06\x07 is the ZIP64_CENTRAL_DIRECTORY_LOCATOR
  #   PK\x05\x06 is the CENTRAL_DIRECTORY_END that we read above

print(">> *.ckpt file looks good!")

# https://github.com/invoke-ai/InvokeAI/blob/4b95c422bde493bf7eb3068c6d3473b0e85a1179/ldm/invoke/model_cache.py#L263-L281
print(f'>> Calculating sha256 hash of the Zip Central Directory from the *.ckpt weights file')

tic = time.time()

# TODO: calculate the SHA256 hash of the CD, or the CD till the rest of the file?
# print("TODO: calculate the SHA256 hash of the CD (or maybe from the CD till the end of the file so it includes EOCD pointers/etc as well?)")
sha = hashlib.sha256()
sha.update(ckpt_cd)
hash = sha.hexdigest()

toc = time.time()

print(f'>> sha256(ckpt_cd) = {hash}','(%4.2fs)' % (toc - tic))

with open(hashpath,'w') as f:
    f.write(hash)
