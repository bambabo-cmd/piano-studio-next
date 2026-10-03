/* Piano Studio Next: small replaceable LGPL-library boundary.
 * This wrapper is original work. GME is Shay Green and contributors' LGPL-2.1+ code.
 * No samples, ROMs or BIOS files are compiled into this wrapper.
 */
#include <cstdint>
#include <cstdlib>
#include <cstring>
#ifndef PSN_NATIVE_063
#include "gme.h"
#else
extern "C" {
struct Music_Emu;
struct gme_info_t { int length,intro_length,loop_length,play_length,fade_length,i5,i6,i7,i8,i9,i10,i11,i12,i13,i14,i15; const char *system,*game,*song,*author,*copyright,*comment,*dumper,*s7,*s8,*s9,*s10,*s11,*s12,*s13,*s14,*s15; };
const char* gme_open_data(const void*,long,Music_Emu**,int);
void gme_delete(Music_Emu*); int gme_track_count(const Music_Emu*);
int gme_voice_count(const Music_Emu*); const char* gme_voice_name(const Music_Emu*,int);
const char* gme_track_info(const Music_Emu*,gme_info_t**,int); void gme_free_info(gme_info_t*);
const char* gme_start_track(Music_Emu*,int); const char* gme_play(Music_Emu*,int,short*);
void gme_mute_voices(Music_Emu*,int); void gme_ignore_silence(Music_Emu*,int);
void gme_set_stereo_depth(Music_Emu*,double); void gme_set_autoload_playback_limit(Music_Emu*,int);
const char* gme_warning(Music_Emu*);
#ifndef PSN_NATIVE_063
void gme_disable_echo(Music_Emu*,int);
#endif
}
#endif
static Music_Emu* emu=nullptr; static gme_info_t* info=nullptr;
static char message[512]={0}; static int rate=32000, voices=0;
static int fail(const char* err){ if(!err)return 0; std::strncpy(message,err,511);message[511]=0;return -1; }
extern "C" {
const char* psn_error(){return message;}
void psn_close(){if(info){gme_free_info(info);info=nullptr;}if(emu){gme_delete(emu);emu=nullptr;}voices=0;}
int psn_open(const unsigned char* data,int size,int sample_rate){psn_close();message[0]=0;if(!data||size<4||size>32*1024*1024||sample_rate!=32000)return fail("Invalid input size or sample rate"); rate=sample_rate;const char* err=gme_open_data(data,size,&emu,rate);if(err){psn_close();return fail(err);}voices=gme_voice_count(emu);if(voices<1||voices>32){psn_close();return fail("Unsupported voice count");}gme_ignore_silence(emu,1);gme_set_autoload_playback_limit(emu,0);gme_set_stereo_depth(emu,0);return 0;}
int psn_tracks(){return emu?gme_track_count(emu):0;}
int psn_voices(){return voices;}
const char* psn_voice_name(int i){return emu&&i>=0&&i<voices?gme_voice_name(emu,i):"";}
int psn_info(int song){if(!emu||song<0||song>=psn_tracks())return fail("Subsong out of range");if(info){gme_free_info(info);info=nullptr;}return fail(gme_track_info(emu,&info,song));}
const char* psn_info_text(int i){if(!info)return ""; switch(i){case 0:return info->system;case 1:return info->game;case 2:return info->song;case 3:return info->author; default:return "";}}
int psn_info_ms(int i){if(!info)return -1;switch(i){case 0:return info->length;case 1:return info->intro_length;case 2:return info->loop_length;default:return info->play_length;}}
const char* psn_warning(){return emu?gme_warning(emu):"";}
int psn_start(int song,int voice,int dry){if(!emu||song<0||song>=psn_tracks()||voice<-1||voice>=voices)return fail("Subsong or voice out of range");gme_ignore_silence(emu,1);gme_set_autoload_playback_limit(emu,0);
 const char* err=gme_start_track(emu,song);if(err)return fail(err);
#ifndef PSN_NATIVE_063
 gme_disable_echo(emu,dry?1:0);
#else
 (void)dry; // The installed native reference library predates this API.
#endif
 const uint32_t mask=voice<0?0u:~(uint32_t(1)<<voice);gme_mute_voices(emu,static_cast<int>(mask));return 0;}
int psn_render(short* pcm,int frames){if(!emu||!pcm||frames<1||frames>16384)return fail("Invalid PCM buffer");return fail(gme_play(emu,frames*2,pcm));}
}
