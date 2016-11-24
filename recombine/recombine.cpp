/*
    sec_tick (1 bit). Is this the first packet for this EDT lane, for this one
        second of data? 0=No, 1=Yes.  Only found on the very first packet of that
        second.  If set, then the mgt_bank, mgt_channel, mgt_group & mgt_frame
        will always be 0.

    pfb_id (2 bits) Which physical fPFB board generated this stream [0-3].
        This defines the set of receivers & tiles the data refers to.
        An EDT lane's pfb_id will remain constant unless physically shifted
        to a different fPFB via a cable swap.

    mgt_id (3 bits) Which 1/8 of coarse channels this rocketIO lane contains.
        Should be masked with 0x7, not 0xf.  Contains [0-7] inclusive.
        An EDT lane's mgt_id will remain constant unless physically shifted
        to a different port on the fPFB via a cable swap.

    Within an EDT lane, the data packets cycle in the following order, listed from
        slowest to fastest.

    mgt_bank (5 bits) Which one of the twenty 50mS time banks in the current
         second is this one? [0-19] [0-0x13].

    mgt_channel (5 bits) Which coarse channel [0-23] [0-0x17] does the packet
        relate to?

    mgt_group (2 bits) Which 40KHz wide packet of the contiguous 160KHz does
         this packet contain the 4 x 10Khz samples for? [0-3]

    mgt_frame (5 bits) Which time stamp within a 50mS block this packet is.
        [0-499] or [0-0x1F3].  Cycles fastest.  Loops back to 0 after 0x1F3.
        There are 20 complete cycles in a second.

        Author: D.Pallot 2014 ICRAR
        Email: dave.pallot@icrar.org
*/


#define _GNU_SOURCE 1

#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <string.h>
#include <sstream>
#include <errno.h>
#include <assert.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/uio.h>
#include <inttypes.h>
#include <limits.h>
#include <dirent.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "fitsio.h"

#include "recombine.h"

static unsigned short byte_to_sum[256] = {
0,1,4,9,16,25,36,49,49,49,36,25,16,9,4,1,1,2,5,10,17,26,37,50,50,50,37,26,17,10,5,2,
4,5,8,13,20,29,40,53,53,53,40,29,20,13,8,5,9,10,13,18,25,34,45,58,58,58,45,34,25,18,13,10,
16,17,20,25,32,41,52,65,65,65,52,41,32,25,20,17,25,26,29,34,41,50,61,74,74,74,61,50,41,34,29,26,
36,37,40,45,52,61,72,85,85,85,72,61,52,45,40,37,49,50,53,58,65,74,85,98,98,98,85,74,65,58,53,50,
49,50,53,58,65,74,85,98,98,98,85,74,65,58,53,50,49,50,53,58,65,74,85,98,98,98,85,74,65,58,53,50,
36,37,40,45,52,61,72,85,85,85,72,61,52,45,40,37,25,26,29,34,41,50,61,74,74,74,61,50,41,34,29,26,
16,17,20,25,32,41,52,65,65,65,52,41,32,25,20,17,9,10,13,18,25,34,45,58,58,58,45,34,25,18,13,10,
4,5,8,13,20,29,40,53,53,53,40,29,20,13,8,5,1,2,5,10,17,26,37,50,50,50,37,26,17,10,5,2
};

#define ICS_BUFF 30720000
#define COURSE_CHAN_BUFF 64000*256

int read_metadata(const char* fitsfilename, course_chan_freq* course_chan_out, tile_flags* tile_flag_out)
{
   fitsfile *fptr;
   char* value;
   int status = 0;

   fits_open_file(&fptr, fitsfilename, READONLY, &status);
   if (status != 0) {
      fits_report_error(stderr, status);
      fits_close_file(fptr, &status);
      return -1;
   }

   status = 0;
   fits_read_key_longstr(fptr, "CHANNELS", &value, NULL, &status);
   if (status != 0) {
      fits_report_error(stderr, status);
      fits_close_file(fptr, &status);
      return -1;
   }

   char chans[1024];
   strcpy(chans, value);
   free(value);

   unsigned int ch_index = 0;
   char* token = NULL;
   char* saveptr = NULL;
   char* ptr = chans;

   while ((token = strtok_r(ptr, ",", &saveptr)) != NULL) {
       course_chan_out->m_freq[ch_index] = atoi(token);
       ch_index++;
       ptr = saveptr;
   }

   if (ch_index != 24) {
      printf("Did not find 24 channels in meta data fits file.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   int anynull, hdutype;
   long int rows = 0;
   status = 0;

   if (fits_movabs_hdu(fptr, 2, &hdutype, &status) != 0) {
      printf("Error moving to binary table in fits file.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   if (hdutype != BINARY_TBL) {
      printf("Binary table not found.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   if (fits_get_num_rows(fptr, &rows, &status) != 0) {
      printf("Could not get number of rows in binary table.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   if (rows != 256) {
      printf("Number of rows in binary table != 256.\n");
      fits_close_file(fptr, &status);
      return -1;
   }
   
   char flagcol[] = "Flag";
   char nullstring[] = "NULL";
   char flags[256];
   int colnum;

   if (fits_get_colnum(fptr, CASEINSEN, flagcol, &colnum, &status) != 0) {
      printf("Could not read flag column from binary table.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   if (fits_read_col(fptr, TBYTE, colnum, 1, 1, 256, nullstring, &flags, &anynull, &status) != 0) {
      printf("Could not read flag data from binary table.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   fits_close_file(fptr, &status);

   memcpy(tile_flag_out->m_flags[0], flags, 64);
   memcpy(tile_flag_out->m_flags[1], flags+64, 64);
   memcpy(tile_flag_out->m_flags[2], flags+128, 64);
   memcpy(tile_flag_out->m_flags[3], flags+192, 64);

   // check our flag table is not all zeros
   unsigned int totalFlagged = 0;

   for (int i = 0; i < 4; ++i) {
      for (int j = 0; j < 64; j++) {
         if (tile_flag_out->m_flags[i][j])
            totalFlagged++;
      }
   }

   if (totalFlagged >= 256) {
      printf("All the tiles are flagged out.\n");
      fits_close_file(fptr, &status);
      return -1;
   }

   return 0;

}


int read_from_input(course_chan_input_matrix* matrix, course_chan_input_array* input, tile_flags* flags)
{
   ssize_t read_in = 0;
   size_t total_read = 0;

   static bool first_run = true;

   if (first_run) {

      for (int i = 0; i < 4; i++)
         for (int j = 0; j < 8; j++) {
            matrix->m_contributing_tiles[i][j] = 64;
            matrix->m_input_matrix[i][j].pad_input = true;
         }

      for (int i = 0; i < 32; ++i) {

         // if there is no stream on this handle then just keep the buffer to all 0's
         if (input->m_handles[i].pad_input == true) {
            continue;
         }

         char* buff = (char*)malloc(VOLT_FILESIZE);
         if (buff == NULL)
            return errno;

         memset(buff, 0, VOLT_FILESIZE);

         read_in = 0;
         total_read = 0;

         while ((read_in = read(input->m_handles[i].m_handle,
                               (buff + total_read),
                               ((VOLT_FILESIZE - total_read) >= BUFFSIZE) ? BUFFSIZE : VOLT_FILESIZE - total_read)) > 0)
         {
            total_read += (size_t)read_in;
         }

         if (total_read != VOLT_FILESIZE)
            return errno;

         //unsigned short w1 = (buff[1] << 8) | buff[0];
         unsigned short w2 = (buff[3] << 8) | buff[2];
         unsigned short w3 = (buff[5] << 8) | buff[4];

         unsigned char freq_index = (w2>>4) & 0x7;
         unsigned char rx_index = (w3>>14) & 0x3;

         //printf("%s %04x %04x %04x %d %d\n", input->m_handles[i].m_id, w1, w2, w3, rx_index, freq_index);

         // Ensure we are in range
         assert(rx_index >= 0 && rx_index <= 3);
         assert(freq_index >= 0 && freq_index <= 7);

         matrix->m_input_matrix[rx_index][freq_index].m_handle = input->m_handles[i].m_handle;
         strcpy(matrix->m_input_matrix[rx_index][freq_index].m_id, input->m_handles[i].m_id);
         matrix->m_input_matrix[rx_index][freq_index].m_buff = buff;
         matrix->m_input_matrix[rx_index][freq_index].pad_input = false;
      }

      unsigned int pfb_tile_flag_count = 0;

      for (int i = 0; i < 4; i++) {

         pfb_tile_flag_count = 0;

         for (int j = 0; j < 64; ++j) {
            if (flags->m_flags[i][j])
               pfb_tile_flag_count++;
         }

         for (int j = 0; j < 8; j++) {
            // if this entry in the matrix does not have a stream, then pad it's buffer with all zeros and make contributing tiles zero
            if (matrix->m_input_matrix[i][j].pad_input == true) {
               char* buff = (char*)malloc(VOLT_FILESIZE);
               if (buff == NULL)
                  return errno;

               memset(buff, 0, VOLT_FILESIZE);

               matrix->m_input_matrix[i][j].m_buff = buff;
               matrix->m_contributing_tiles[i][j] = 0;
            }
            else
            {
               matrix->m_contributing_tiles[i][j] -= pfb_tile_flag_count;
            }
         }
      }

      first_run = false;
   }
   else
   {
      for (int i = 0; i < 4; i++)
         for (int j = 0; j < 8; j++) {

            // don't want to read from the handle if there is no stream behind it
            if (matrix->m_input_matrix[i][j].pad_input == true)
               continue;

            read_in = 0;
            total_read = 0;

            while ((read_in = read(matrix->m_input_matrix[i][j].m_handle,
                                  (matrix->m_input_matrix[i][j].m_buff + total_read),
                                  ((VOLT_FILESIZE - total_read) >= BUFFSIZE) ? BUFFSIZE : VOLT_FILESIZE - total_read)) > 0)
            {
               total_read += (size_t)read_in;
            }

            if (total_read != VOLT_FILESIZE)
               return errno;
         }
   }

   return 0;
}


void course_channel_swap(const course_chan_freq* in, course_chan_freq* out, unsigned int* course_swap_index)
{
   unsigned int freq[24];

   memcpy(freq, in->m_freq, sizeof(freq));

   unsigned int temp;

   for(int i = 0; i < 24; i++)
   {
      for(int j = i; j < 24;j++)
      {
         if(freq[i] > freq[j])
         {
            temp = freq[i];
            freq[i] = freq[j];
            freq[j] = temp;
         }
      }
   }

   // no channels to swap
   *course_swap_index = 24;

   // find the index where the channels are swapped i.e. where 129 exists
   for (int i = 0; i < 24; ++i) {
      if (freq[i] >= 129) {
         *course_swap_index = i;
         break;
      }
   }

   // keep the order the same on output because we are swapping the
   // data not the labels;
   for (int i = 0; i < 24; ++i) {
      out->m_freq[i] = freq[i];
   }

}


int recombine(course_chan_input_array* input, course_chan_output_array* output, ics_handle* ics_out, unsigned int course_swap_index, tile_flags* flags, bool skipics, bool skipcourse)
{
   int retcode = 0;

   course_chan_input_matrix inputs;

   memset(&inputs, 0, sizeof(course_chan_input_matrix));

   unsigned int header_offset = 6;

   // create file buffer
   char* file_buffer[24];
   uint64_t file_buffer_index[24];

   for (int b = 0; b < 24; b++) {
      file_buffer[b] = (char*)valloc(COURSE_CHAN_BUFF);
      if (file_buffer[b] == NULL)
         return errno;
   }

   unsigned short deadblocks = 0;
   unsigned short ics = 0;
   unsigned char ics_byte = 0;
   char* mem = NULL;

   int64_t t_sample_offset = 0;
   int64_t course_chan_offset = 0;
   int64_t freq_group_offset = 0;
   int64_t ten_kHz_offset = 0;

   char* ics_buffer = NULL;
   uint64_t ics_buffer_index = 0;

   if (!skipics) {
      ics_buffer = (char*)valloc(ICS_BUFF);
      if (ics_buffer == NULL) {
         retcode = errno;
         goto Error;
      }
   }

   // Read in 50ms chunks which is 48000 packets
   for (int ms = 0; ms < 20; ms++) {

      memset(file_buffer_index, 0, sizeof(file_buffer_index));

      int read = read_from_input(&inputs, input, flags);
      if (read < 0) {
         retcode = errno;
         goto Error;
      }

      for (int t_sample = 0; t_sample < 500; ++t_sample) {
         t_sample_offset = t_sample * 264;

         for (int course_ch = 0; course_ch < 24; ++course_ch) {
            if (course_ch < course_swap_index)
               course_chan_offset = course_ch * 4 * 500 * 264;
            else
               course_chan_offset = (23-course_ch+course_swap_index) * 4 * 500 * 264;

            for (int lane_id = 0; lane_id < 8; ++lane_id) {

               for (int freq_grp = 0; freq_grp < 4; ++freq_grp) {
                  freq_group_offset = freq_grp * 500 * 264;

                  for (int ten_kHz = 0; ten_kHz < 4; ++ten_kHz) {
                     ten_kHz_offset = ten_kHz * 64;

                     ics = 0;
                     deadblocks = 0;

                     for (int pfb_no = 0; pfb_no < 4; ++pfb_no) {

                        // start of packet
                        mem = inputs.m_input_matrix[pfb_no][lane_id].m_buff + t_sample_offset + course_chan_offset + freq_group_offset + ten_kHz_offset + header_offset;

                        if (!skipcourse) {
                           memcpy((file_buffer[course_ch]+file_buffer_index[course_ch]), mem, 64);
                           file_buffer_index[course_ch] += 64;
                        }

                        if (!skipics) {
                           if (inputs.m_input_matrix[pfb_no][lane_id].pad_input) {
                              deadblocks += 1;
                           }
                           else {
                              for (unsigned int tile = 0; tile < 64; ++tile) {
                                 if (flags->m_flags[pfb_no][tile] == 0)
                                    // was:  ics += byte_to_sum[(unsigned char)mem[tile]];
                                    ics += byte_to_sum[(unsigned char)mem[((tile&0x30)>>4)|((tile&0x0f)<<2)]];
                                           // m_flags is sorted in tile order 0,1,2,3,4... The mem array is sorted 0,16,32,48,1,17,33,49,2,18,…,15,31,47,63
                                           // The complex dereferencing for the mem array index is to undo this weird order that fPFB sorts it into
                                           // See ICD_PFB_CB_32T.doc for more detail.

                              }
                           }
                        }

                     } // end 4 lots of 64

                     if (!skipics) {

                        unsigned int tile_contrib_for_lane = 0;
                        for (int i = 0; i < 4; ++i)
                           tile_contrib_for_lane += inputs.m_contributing_tiles[i][lane_id];

                        // normalisation: if at least 1 input has data then we will scale for missing inputs
                        if (tile_contrib_for_lane > 0) {
                           // 5: the number that Dr Brian (1st class honors Magnetic Therapy) pulled out of somewhere
                           // vague justification: if avg amplitude was the maximum allowed at any phase then total sum would still fit in one byte (char)
                           // (256-deadblocks*64): normalise based on the number of contributing tiles
                           //ics = (ics * 5) / (256-deadblocks*64);

                           ics = (ics * 5) / tile_contrib_for_lane;
                           if (ics > 255)
                              ics = 255; // clipping to a bytes worth for demotion to char; should only occur once other parts of system are non-linear

                           ics_byte = (unsigned char)(ics);

                           //ics_byte = (unsigned char)(ics / (256-deadblocks*64));
                        }
                        else
                           // if there are not inputs at all for the 10kHz channel then we set the sum to zero
                           ics_byte = 0;

                        // copy ics 1 byte value into buffer
                        memcpy(ics_buffer+ics_buffer_index, &ics_byte, sizeof(unsigned char));
                        //ics_buffer[ics_buffer_index] = ics_byte;
                        ics_buffer_index += sizeof(unsigned char);
                     }

                  }

               }
            }

         }

      }

      if (!skipcourse) {

         ssize_t written = 0;
         size_t total_written = 0;

         //write out each course channel
         for (int c = 0; c < 24; c++) {

            written = 0;
            total_written = 0;

            while ((written = write(output->m_handles[c].m_handle,
                                    file_buffer[c]+total_written,
                                    (COURSE_CHAN_BUFF-total_written) >= BUFFSIZE ? BUFFSIZE : COURSE_CHAN_BUFF-total_written)) > 0)
            {
               total_written += (size_t)written;
            }

            if (total_written != COURSE_CHAN_BUFF) {
               retcode = errno;
               goto Error;
            }

         }
      }

   } // end 20ms chunks


   if (!skipics) {

      // write out ics buffers
      ssize_t written_ics = 0;
      size_t total_written_ics = 0;

      while ((written_ics = write(ics_out->m_handle,
                                  ics_buffer+total_written_ics,
                                  (ICS_BUFF-total_written_ics) >= BUFFSIZE ? BUFFSIZE : ICS_BUFF-total_written_ics)) > 0)
      {
         total_written_ics += (size_t)written_ics;
      }

      if (total_written_ics != ICS_BUFF) {
         retcode = errno;
         goto Error;
      }
   }


Error:
   for (int i = 0; i < 4; i++)
      for (int j = 0; j < 8; j++)
         free(inputs.m_input_matrix[i][j].m_buff);

   for (int b = 0; b < 24; b++)
      free(file_buffer[b]);

   if (!skipics)
      free(ics_buffer);

   return retcode;
}

int open_input_from_directory(const char* directory, course_chan_input_array* input)
{
   unsigned int count = 0;

   struct dirent *ep;

   DIR* dp = opendir(directory);

   if (dp != NULL) {
      while ( (ep = readdir(dp)) ) {
         std::string name(ep->d_name);
         if (name == "." || name == "..")
            continue;

         strcpy(input->m_handles[count].m_id, ep->d_name);

         std::string full = std::string(directory) + "/" + name;
         if ((input->m_handles[count].m_handle = open(full.c_str(), O_RDONLY)) < 0) {
            input->m_handles[count].pad_input = true; // input failed to open; pad stream with zeros
         }
         /*else {
            struct stat st;
            assert(fstat(input->m_handles[count].m_handle, &st) != -1);
            posix_fadvise(input->m_handles[count].m_handle, 0, st.st_size, POSIX_FADV_SEQUENTIAL|POSIX_FADV_WILLNEED);
         }*/

         count+=1;

         // we can not exceed 32 input files
         if (count >= 32)
            break;

      }

      closedir(dp);
   }
   else {
      perror("Couldn't open the directory\n");
      return errno;
   }

   return 0;
}


int open_input_from_file_list(const char* input_file_list, course_chan_input_array* input)
{
   FILE *fp;
   char *line = NULL;
   size_t len = 0;
   ssize_t read;
   unsigned int count = 0;

   fp = fopen(input_file_list, "r");
   if (fp == NULL)
      exit(EXIT_FAILURE);

   while ((read = getline(&line, &len, fp)) != -1 && count < 32) {

      if (line[strlen(line) - 1] == '\n')
         line[strlen(line)-1] = 0;

      strcpy(input->m_handles[count].m_id, line);

      count += 1;
   }

   free(line);

   return open_input_from_file(input);
}


int open_input_from_file(course_chan_input_array* input)
{
   for (int i = 0; i < 32; ++i)
      if ((input->m_handles[i].m_handle = open(input->m_handles[i].m_id, O_RDONLY)) < 0) {
         input->m_handles[i].pad_input = true; // input failed to open; pad stream with zeros
      }
      /*else {
         struct stat st;
         assert(fstat(input->m_handles[i].m_handle, &st) != -1);
         posix_fadvise(input->m_handles[i].m_handle, 0, st.st_size, POSIX_FADV_SEQUENTIAL|POSIX_FADV_WILLNEED);
      }*/

   return 0;
}


int open_output_to_file(course_chan_output_array* output)
{
   for (int i = 0; i < 24; i++)
      if ((output->m_handles[i].m_handle = open(output->m_handles[i].m_id, O_WRONLY | O_CREAT | O_TRUNC, (S_IRWXU | S_IRGRP))) < 0)
         return errno;

   return 0;
}


void close_input_handles(course_chan_input_array* input)
{
   int ret = 0;
   for (int i = 0; i < 24; ++i) {
      ret = close(input->m_handles[i].m_handle);
   }
}

void close_output_handles(course_chan_output_array* output)
{
   int ret = 0;
   for (int i = 0; i < 24; ++i) {
      ret = close(output->m_handles[i].m_handle);
   }
}
