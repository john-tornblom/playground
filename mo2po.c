/* Copyright (C) 2021 John Törnblom
   
   Parser for gettext MO files, as described on:
   https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html
*/

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>


#define MO_MAGIC 0x950412de


/**
 * All MO files starts with a header.
 **/
typedef struct mo_head {
  uint32_t magic;
  struct {
    uint16_t major;
    uint16_t minor;
  } revision;
  
  uint32_t nb_mappings;
  uint32_t src_offset;
  uint32_t dst_offset;
} mo_head_t;


/**
 * The header points at entries that describe string values.
 **/
typedef struct mo_entry {
  uint32_t length;
  uint32_t offset;
} mo_entry_t;


/**
 * Entries in a MO file are used to map string keys to string values.
 **/
typedef struct string_map {
  char *key;
  char *val;
} string_map_t;


/**
 * Given a pointer to a MO file, parse its content into a string map.
 *
 * Upon success, zero is returned. When an error occurs, *map and 
 * *nb_mappings are set to zero, and a non-zero value is returned.
 **/
int
mo_parse(FILE* fp, string_map_t **map, uint32_t *nb_mappings) {
  mo_head_t head;
  *nb_mappings = 0;
  *map = 0;
  
  // Read header and do sanity checks
  if(fread(&head, sizeof(mo_head_t), 1, fp) != 1) {
    return -1;
  }

  if(head.magic != MO_MAGIC) {
    return -1; // not a MO file
  }

  if(head.revision.major > 1 || head.revision.minor > 1) {
    return -1; // unsupported revision
  }

  // Read entries of source strings
  mo_entry_t src[head.nb_mappings];
  if(fseek(fp, head.src_offset, SEEK_SET)) {
    return -1;
  }
  if(fread(src, sizeof(mo_entry_t), head.nb_mappings, fp) != head.nb_mappings) {
    return -1;
  }

  // Read entries of target strings
  mo_entry_t dst[head.nb_mappings];
  if(fseek(fp, head.dst_offset, SEEK_SET)) {
    return -1;
  }
  if(fread(dst, sizeof(mo_entry_t), head.nb_mappings, fp) != head.nb_mappings) {
    return -1;
  }

  // Allocate heap memory for caller
  if(!(*map = calloc(head.nb_mappings, sizeof(string_map_t)))) {
    return -1;
  }

  int error = 0;
  for(uint32_t i=0; i<head.nb_mappings; i++) {
    // Read key string
    if(!((*map)[i].key = calloc(src[i].length + 1, sizeof(char)))) {
      error = -1; break;
    }    
    if(fseek(fp, src[i].offset, SEEK_SET)) {
      error = -1; break;
    }
    if(fread((*map)[i].key, sizeof(char), src[i].length, fp) != src[i].length) {
      error = -1; break;
    }

    // Read value string
    if(!((*map)[i].val = calloc(dst[i].length + 1, sizeof(char)))) {
      error = -1; break;
    }
    if(fseek(fp, dst[i].offset, SEEK_SET)) {
      error = -1; break;
    }
    if(fread((*map)[i].val, sizeof(char), dst[i].length, fp) != dst[i].length) {
      error = -1; break;
    }
  }

  if(!error) {
    *nb_mappings = head.nb_mappings;
    return 0;
  }
  
  // Something went wrong, free memory allocated on the heap
  for(uint32_t i=0; i<head.nb_mappings; i++) {
    if((*map)[i].key) {
      free((*map)[i].key);
    }
    if((*map)[i].val) {
      free((*map)[i].val);
    }
  }

  free(*map);
  *map = 0;
  
  return error;
}


/**
 * Dump a string to stdout in its C-escaped format.
 **/
static void
dump_string(const char* str) {
  size_t i = 0;
  size_t maxlen = strlen(str);
  
  fprintf(stdout, "\"");

  while(i < maxlen) {
    switch(str[i]) {
    case '\a':
      fprintf(stdout, "\\a");
      break;

    case '\b':
      fprintf(stdout, "\\b");
      break;

    case '\e':
      fprintf(stdout, "\\e");
      break;

    case '\f':
      fprintf(stdout, "\\f");
      break;

    case '\n':
      fprintf(stdout, "\\n");
      break;

    case '\r':
      fprintf(stdout, "\\r");
      break;

    case '\t':
      fprintf(stdout, "\\t");
      break;

    case '\v':
      fprintf(stdout, "\\v");
      break;

    case '\\':
      fprintf(stdout, "\\\\");
      break;

      /*
    case '\'':
      fprintf(stdout, "\\\'");
      break;

    case '\?':
      fprintf(stdout, "\\?");
      break;
      */

    case '\"':
      fprintf(stdout, "\\\"");
      break;

    case '\0':
      i = maxlen;
      break;

    default:
      fprintf(stdout, "%c", str[i]);
    }
    i++;
  }

  fprintf(stdout, "\"\n");
}


int main(int argc, char** argv) {
  uint32_t nb_mappings;
  string_map_t *map;
  FILE *fp;
  
  if(argc <= 1) {
    fprintf(stderr, "usage: %s file1.mo [file2.mo ...]\n", argv[0]);
    return 1;
  }

  for(int i=1; i<argc; i++) {
    if(!(fp = fopen(argv[i], "rb"))) {
      perror(argv[i]);
      continue;
    }
    
    mo_parse(fp, &map, &nb_mappings);
    
    for(int i=0; i<nb_mappings; i++) {
      fprintf(stdout, "msgid ");
      dump_string(map[i].key);
      
      fprintf(stdout, "msgstr ");
      dump_string(map[i].val);
      fprintf(stdout, "\n");
    }
  }
  return 0;
}
