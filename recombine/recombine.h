/*
 * recombine.h
 *
 *  Created on: 06/06/2014
 *      Author: dpallot
 */

#ifndef RECOMBINE_H_
#define RECOMBINE_H_

#include <string>
#include <stdio.h>


#define PACKETS_PER_50MS 48000
#define PACKET_SIZE_BYTES 264
#define BYTES_PER_SEC (PACKETS_PER_50MS * PACKET_SIZE_BYTES * 20)
#define VOLT_FILESIZE (PACKETS_PER_50MS * PACKET_SIZE_BYTES)
#define BUFFSIZE 1048576

typedef struct course_chan_input {
	int m_handle;
	char m_id[1024];
	bool pad_input;
	char* m_buff;
} course_chan_input_t;


typedef struct course_chan_input_handle {
	int m_handle;
	char m_id[1024];
	bool pad_input;
	char* m_buff;
} course_chan_input_handle_t;

typedef struct course_chan_input_array {
	course_chan_input_handle m_handles[32];

} course_chan_input_array_t;

typedef struct course_chan_input_matrix {
	course_chan_input_t m_input_matrix[4][8];
	unsigned short m_contributing_tiles[4][8];
} course_chan_input_matrix_t;


typedef struct course_chan_output_handle {
	int m_handle;
	char m_id[1024];
} course_chan_output_handle_t;


typedef struct course_chan_output_array {
	course_chan_output_handle m_handles[24];

} course_chan_output_array_t;

typedef struct ics_handle {
	int m_handle;
} ics_handle_t;


typedef struct course_chan_freq {
	unsigned int m_freq[24];
} course_chan_freq_t;

// PFB board x dipole (0: keep 1: flag out)
typedef struct tile_flags {
	char m_flags[4][64];
} tile_flags_t;

// course_chan_freq* in: must be continuous 24 course channels
// course_swap_index: 24 if there are no channels to swap
void course_channel_swap(const course_chan_freq* in, course_chan_freq* out, unsigned int* course_swap_index);

int recombine(course_chan_input_array* input, course_chan_output_array* output, ics_handle* ics_out, unsigned int course_swap_index, tile_flags* flags, bool skipics, bool skipcourse);
int read_from_input(course_chan_input_matrix* matrix, course_chan_input_array* input, tile_flags* flags);

int open_input_from_directory(const char* directory, course_chan_input_array* input);
int open_input_from_file_list(const char* input_file_list, course_chan_input_array* input);
int open_input_from_file(course_chan_input_array* input);
int open_output_to_file(course_chan_output_array* output);

int read_metadata(const char* fitsfile, course_chan_freq* course_chan_out, tile_flags* tile_flag_out);

void close_input_handles(course_chan_input_array* input);
void close_output_handles(course_chan_output_array* output);

#endif /* RECOMBINE_H_ */
