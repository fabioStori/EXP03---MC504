import ctypes
import re
import pandas as pd
import sys
from math import ceil

file_system = open(sys.argv[1], 'rb')

class Ext3Superblock(ctypes.Structure):
    _fields_ = [
        ('s_inodes_count', ctypes.c_int32),   # /* Inodes count */
        ('s_blocks_count', ctypes.c_int32),   # /* Blocks count */
        ('s_r_blocks_count', ctypes.c_int32),   # /* Reserved blocks count */
        ('s_free_blocks_count', ctypes.c_int32),   # /* Free blocks count */S
        ('s_free_inodes_count', ctypes.c_int32),   # /* Free inodes count */
        ('s_first_data_block', ctypes.c_int32),   # /* First Data Block */
        ('s_log_block_size', ctypes.c_int32),   # /* Block size */  <- block_size = 2 ^ (10 + s_log_block_size)
        ('s_log_frag_size', ctypes.c_int32),   # /* Fragment size */ < - frag_size = 2 ^ (10 + s_log_frag_size)
        ('s_blocks_per_group', ctypes.c_int32),   # /* # Blocks per group */
        ('s_frags_per_group', ctypes.c_int32),   # /* # Fragments per group */
        ('s_inodes_per_group', ctypes.c_int32),   # /* # Inodes per group */
        ('s_mtime', ctypes.c_int32),   # /* Mount time */
        ('s_wtime', ctypes.c_int32),   # /* Write time */
        ('s_mnt_count', ctypes.c_int16),   # /* Mount count */
        ('s_max_mnt_count', ctypes.c_int16),   # /* Maximal mount count */
        ('s_magic', ctypes.c_int16),   # /* Magic signature */
        ('s_state', ctypes.c_int16),   # /* File system state */
        ('s_errors', ctypes.c_int16),   # /* Behaviour when detecting errors */
        ('s_minor_rev_level', ctypes.c_int16),   # /* minor revision level */
        ('s_lastcheck', ctypes.c_int32),   # /* time of last check */
        ('s_checkinterval', ctypes.c_int32),   # /* max. time between checks */
        ('s_creator_os', ctypes.c_int32),   # /* OS */
        ('s_rev_level', ctypes.c_int32),   # /* Revision level */
        ('s_def_resuid', ctypes.c_int16),   # /* Default uid for reserved blocks */
        ('s_def_resgid', ctypes.c_int16),   # /* Default gid for reserved blocks */
        ('s_first_ino', ctypes.c_int32),   # /* First non-reserved inode */
        ('s_inode_size', ctypes.c_int16),   # /* size of inode structure */
        ('s_block_group_nr', ctypes.c_int16),   # /* block group # of this superblock */
        ('s_feature_compat', ctypes.c_int32),   # /* compatible feature set */
        ('s_feature_incompat', ctypes.c_int32),   # /* incompatible feature set */
        ('s_feature_ro_compat', ctypes.c_int32),   # /* readonly-compatible feature set */
        ('s_uuid', ctypes.c_uint8 * 16),   # /* 128-bit uuid for volume */
        ('s_volume_name', ctypes.c_char * 16),   # /* volume name */
        ('s_last_mounted', ctypes.c_char * 64),   # /* directory where last mounted */
        ('s_algorithm_usage_bitmap', ctypes.c_int32),   # /* For compression */
        ('s_prealloc_blocks', ctypes.c_uint8),   # /* Nr of blocks to try to preallocate*/
        ('s_prealloc_dir_blocks', ctypes.c_uint8),   # /* Nr to preallocate for dirs */
        ('s_reserved_gdt_blocks', ctypes.c_int16),   # /* Per group desc for online growth */
        ('s_journal_uuid', ctypes.c_uint8 * 16),   # /* uuid of journal superblock */
        ('s_journal_inum', ctypes.c_int32),   # /* inode number of journal file */
        ('s_journal_dev', ctypes.c_int32),   # /* device number of journal file */
        ('s_last_orphan', ctypes.c_int32),   # /* start of list of inodes to delete */
        ('s_hash_seed', ctypes.c_int32 * 4),   # /* HTREE hash seed */
        ('s_def_hash_version', ctypes.c_uint8),   # /* Default hash version to use */
        ('s_reserved_char_pad', ctypes.c_uint8),   
        ('s_reserved_word_pad', ctypes.c_uint16),   
        ('s_default_mount_opts', ctypes.c_int32),   
        ('s_first_meta_bg', ctypes.c_int32),   # /* First metablock block group */
        ('s_mkfs_time', ctypes.c_int32),   # /* When the filesystem was created */
        ('s_jnl_blocks', ctypes.c_int32 * 17),   # /* Backup of the journal inode */
        ('s_blocks_count_hi', ctypes.c_int32),   # /* Blocks count */
        ('s_r_blocks_count_hi', ctypes.c_int32),   # /* Reserved blocks count */
        ('s_free_blocks_count_hi', ctypes.c_int32),   # /* Free blocks count */
        ('s_min_extra_isize', ctypes.c_int16),   # /* All inodes have at least # bytes */
        ('s_want_extra_isize', ctypes.c_int16),   # /* New inodes should reserve # bytes */
        ('s_flags', ctypes.c_int32),   # /* Miscellaneous flags */
        ('s_raid_stride', ctypes.c_int16),   # /* RAID stride */
        ('s_mmp_interval', ctypes.c_int16),   # /* # seconds to wait in MMP checking */
        ('s_mmp_block', ctypes.c_int64),   # /* Block for multi-mount protection */
        ('s_raid_stripe_width', ctypes.c_int32),   # /* blocks on all data disks (N*stride)*/
        ('s_log_groups_per_flex', ctypes.c_uint8),   # /* FLEX_BG group size */
        ('s_reserved_char_pad2', ctypes.c_uint8),   
        ('s_reserved_pad', ctypes.c_int16),   
        ('s_reserved', ctypes.c_uint32 * 162),   # /* Padding to the end of the block */
    ]
    
class Ext3BlockGroupDescriptor(ctypes.Structure):
    _fields_ = [
        ('bg_block_bitmap', ctypes.c_int32),   # /* Blocks bitmap block */
        ('bg_inode_bitmap', ctypes.c_int32),   # /* Inodes bitmap block */
        ('bg_inode_table', ctypes.c_int32),   # /* Inodes table block */
        ('bg_free_blocks_count', ctypes.c_int16),   # /* Free blocks count */
        ('bg_free_inodes_count', ctypes.c_int16),   # /* Free inodes count */
        ('bg_used_dirs_count', ctypes.c_int16),   # /* Directories count */
        ('bg_pad', ctypes.c_uint16),   
        ('bg_reserved', ctypes.c_int32 * 3),  
    ]

EXT3_NDIR_BLOCKS = 12
EXT3_IND_BLOCK = EXT3_NDIR_BLOCKS
EXT3_DIND_BLOCK = (EXT3_IND_BLOCK + 1)
EXT3_TIND_BLOCK = (EXT3_DIND_BLOCK + 1)
EXT3_N_BLOCKS = (EXT3_TIND_BLOCK + 1)

class _linux1(ctypes.Structure):
     _fields_ = [('l_i_reserved1', ctypes.c_uint32)] 

class _hurd1(ctypes.Structure):
     _fields_ = [('h_i_translator', ctypes.c_uint32)] 
        
class _masix1(ctypes.Structure):
     _fields_ = [('m_i_reserved1', ctypes.c_uint32)]
        
class _osd1(ctypes.Union):
     _fields_ = [("linux1", _linux1),
                 ("hurd1", _hurd1),
                 ("masix1", _masix1)]

        
class _linux2(ctypes.Structure):
     _fields_ = [
        ('l_i_frag', ctypes.c_uint8),   # /* Fragment number */
        ('l_i_fsize', ctypes.c_uint8),   # /* Fragment size */
        ('i_pad1', ctypes.c_uint16),   
        ('l_i_uid_high', ctypes.c_int16),   # /* these 2 fields    */
        ('l_i_gid_high', ctypes.c_int16),   # /* were reserved2[0] */
        ('l_i_reserved2', ctypes.c_uint32),   
     ] 

class _hurd2(ctypes.Structure):
     _fields_ = [        
         ('h_i_frag', ctypes.c_uint8),   # /* Fragment number */
         ('h_i_fsize', ctypes.c_uint8),   # /* Fragment size */
         ('h_i_mode_high', ctypes.c_uint16),   
         ('h_i_uid_high', ctypes.c_uint16),   
         ('h_i_gid_high', ctypes.c_uint16),   
         ('h_i_author', ctypes.c_uint32)
     ]
        
class _masix2(ctypes.Structure):
     _fields_ = [
        ('m_i_frag', ctypes.c_uint8),   # /* Fragment number */
        ('m_i_fsize', ctypes.c_uint8),   # /* Fragment size */
        ('m_pad1', ctypes.c_uint16),   
        ('m_i_reserved2', ctypes.c_uint32 * 2),   
     ]
        
class _osd2(ctypes.Union):
     _fields_ = [("linux2", _linux1),
                 ("hurd2", _hurd1),
                 ("masix2", _masix1)]
        
class Ext3Inode(ctypes.Structure):
    _fields_ = [
        #('i_mode', ctypes.c_int16),   # /* File mode */
        ('i_mode', ctypes.c_uint16),
        ('i_uid', ctypes.c_int16),   # /* Low 16 bits of Owner Uid */
        ('i_size', ctypes.c_int32),   # /* Size in bytes */
        ('i_atime', ctypes.c_int32),   # /* Access time */
        ('i_ctime', ctypes.c_int32),   # /* Creation time */
        ('i_mtime', ctypes.c_int32),   # /* Modification time */
        ('i_dtime', ctypes.c_int32),   # /* Deletion Time */
        ('i_gid', ctypes.c_int16),   # /* Low 16 bits of Group Id */
        ('i_links_count', ctypes.c_int16),   # /* Links count */
        ('i_blocks', ctypes.c_int32),   # /* Blocks count */ blocks of 512 bytes! 
        ('i_flags', ctypes.c_int32),   # /* File flags */
        ('osd1', _osd1), # /* OS dependent 1 */ 
        ('i_block', ctypes.c_int32 * EXT3_N_BLOCKS), # /* Pointers to blocks */
        ('i_generation', ctypes.c_int32),   # /* File version (for NFS) */
        ('i_file_acl', ctypes.c_int32),   # /* File ACL */
        ('i_dir_acl', ctypes.c_int32),   # /* Directory ACL */
        ('i_faddr', ctypes.c_int32),   # /* Fragment address */
        ('osd2', _osd2), # /* OS dependent 2 */ 
        ('i_extra_isize', ctypes.c_int16),   
        ('i_pad1', ctypes.c_int16),   
    ]

everest_superblock = Ext3Superblock()

file_system.seek(1024)
file_system.readinto(everest_superblock)

BLOCK_SIZE = 2 ** (10 + everest_superblock.s_log_block_size)

POINTERS_ON_INODE_INDIRECT = int(BLOCK_SIZE/4)
class Ext3InodeIndirect(ctypes.Structure):
    _fields_ = [('i_block', ctypes.c_int32 * POINTERS_ON_INODE_INDIRECT)]

INODE_BLOCKS_PER_GROUP = int((everest_superblock.s_inodes_per_group * everest_superblock.s_inode_size)/BLOCK_SIZE)

#(everest_superblock.s_blocks_count * BLOCK_SIZE)/(2**30)  # tamanho aproximado em GB, ainda tem alguns bytes a se considerar

NUMBER_OF_GROUPS = ceil(everest_superblock.s_blocks_count / everest_superblock.s_blocks_per_group)


class Ext3BlockGroupDescriptorTable(ctypes.Structure):
    _fields_ = [("block_group_descriptor", Ext3BlockGroupDescriptor * (NUMBER_OF_GROUPS))]

BLOCKS_IN_LAST_GROUP = everest_superblock.s_blocks_count % everest_superblock.s_blocks_per_group

# simple function using shifts to get the n bit from the x uint
get_bit = lambda x,n: (x & (1<<n)) >> n

# to read the block and the inode bitmap we need to read the bits in the following order: 
# read every byte from left to right, but the bits from right to left
# eg: 
# hex:         0x403C
# binary:      01000000 00111100
# read_order:  00000010 00111100

# that's the same as reading the value as a little endian int and follow each byte
#print("".join(map(str,[get_bit(int.from_bytes(b'\x40\x3c', 'little'),i) for i in range(16)])))

    # The first block of this block group is represented by bit 0 of byte 0, the second by bit 1 of byte 0. 
    # The 8th block is represented by bit 7 (most significant bit) of byte 0 while the 9th block is represented by bit 0 
    #(least significant bit) of byte 1.

# lendo block group descriptor table
file_system.seek(BLOCK_SIZE)
everest_descriptor_table = Ext3BlockGroupDescriptorTable()
file_system.readinto(everest_descriptor_table)

total_used_blocks = 0
total_free_blocks = 0
total_used_inodes = 0
total_free_inodes = 0

block_free_segments_number = 0
block_segments_control = False # this variable will assist us into computing the number of free segments

inode_segments_count = 0

file_sizes = [] # here we will concatenate all sizes so we can build the table at the end
inode_segs = []

for group in range(NUMBER_OF_GROUPS):
    # localização do inode bitmap e inode table para cada grupo
#     print(everest_descriptor_table.block_group_descriptor[group].bg_inode_bitmap, 
#            everest_descriptor_table.block_group_descriptor[group].bg_inode_table)
    block_bitmap_location = everest_descriptor_table.block_group_descriptor[group].bg_block_bitmap * BLOCK_SIZE
    inode_bitmap_location = everest_descriptor_table.block_group_descriptor[group].bg_inode_bitmap * BLOCK_SIZE
    inode_table_location = everest_descriptor_table.block_group_descriptor[group].bg_inode_table * BLOCK_SIZE
    
    # inode_table_location += everest_superblock.s_first_ino * everest_superblock.s_inode_size
        
    # blocks
    file_system.seek(block_bitmap_location)
    entry = file_system.read(ceil(everest_superblock.s_blocks_per_group/8))
    entry_uint = int.from_bytes(entry, 'little') 
    
    n_blocks = everest_superblock.s_blocks_per_group if group != NUMBER_OF_GROUPS-1 else BLOCKS_IN_LAST_GROUP
    for i in range(n_blocks):
        if block_segments_control:
            if get_bit(entry_uint, i): # end of a segment
                block_segments_control = False
        else:
            if not get_bit(entry_uint, i): # start of a segment
                block_segments_control = True
                block_free_segments_number += 1
        
    if group != NUMBER_OF_GROUPS-1:
        total_used_blocks += sum([1 for i in range(everest_superblock.s_blocks_per_group) if get_bit(entry_uint, i)])
        total_free_blocks += sum([1 for i in range(everest_superblock.s_blocks_per_group) if not get_bit(entry_uint, i)])
    else:
        total_used_blocks += sum([1 for i in range(BLOCKS_IN_LAST_GROUP) if get_bit(entry_uint, i)])
        total_free_blocks += sum([1 for i in range(BLOCKS_IN_LAST_GROUP) if not get_bit(entry_uint, i)])
        
    # inodes
    file_system.seek(inode_bitmap_location)
    entry = file_system.read(ceil(everest_superblock.s_inodes_count/8))
    entry_uint = int.from_bytes(entry, 'little') 
        
    total_used_inodes += sum([1 for i in range(everest_superblock.s_inodes_per_group) if get_bit(entry_uint, i)])
    total_free_inodes += sum([1 for i in range(everest_superblock.s_inodes_per_group) if not get_bit(entry_uint, i)])
    
    #file_system.seek(inode_table_location)
    for i in range(everest_superblock.s_inodes_per_group):
        if i < everest_superblock.s_first_ino:
            continue
        if get_bit(entry_uint, i): # inode is occupied
            file_system.seek(inode_table_location + i*everest_superblock.s_inode_size)
            inode = Ext3Inode()
            file_system.readinto(inode)
            
            # here read the inode content into an i-block
            n_blocks = inode.i_blocks
#             file_system.seek(inode_table_location + i*everest_superblock.s_inode_size)
#             print(file_system.read(128))
            n_used_blocks = int((inode.i_blocks * 512)/BLOCK_SIZE)
    
            used_blocks = [inode.i_block[j] for j in range(15) if inode.i_block[j]]
            
            
            if n_used_blocks > 12:
                #process indirect on 13th block
                indirect = Ext3InodeIndirect()
                file_system.seek(inode.i_block[12] * BLOCK_SIZE)
                file_system.readinto(indirect)
                # add [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT)]
                used_blocks += [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT) if indirect.i_block[j]]
                
            if n_used_blocks > 12 + POINTERS_ON_INODE_INDIRECT:
                #process double indirect on 14th block
                indirect = Ext3InodeIndirect()
                file_system.seek(inode.i_block[13] * BLOCK_SIZE)
                file_system.readinto(indirect)
                # add [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT)]
                used_blocks += [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT) if indirect.i_block[j]]
                for j in range(POINTERS_ON_INODE_INDIRECT):
                    if not indirect.i_block[j]:
                        continue
                    double_indirect = Ext3InodeIndirect()
                    file_system.seek(indirect.i_block[j] * BLOCK_SIZE)
                    file_system.readinto(double_indirect)
                    # add [double_indirect.i_block[k] for k in range(POINTERS_ON_INODE_INDIRECT)]
                    used_blocks += [double_indirect.i_block[k] for k in range(POINTERS_ON_INODE_INDIRECT) if double_indirect.i_block[k]]
                
            if n_used_blocks > 12 +POINTERS_ON_INODE_INDIRECT + POINTERS_ON_INODE_INDIRECT**2:
                #process triple indirect on 15th block
                indirect = Ext3InodeIndirect()
                file_system.seek(inode.i_block[14] * BLOCK_SIZE)
                file_system.readinto(indirect)
                # add [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT)]
                used_blocks += [indirect.i_block[j] for j in range(POINTERS_ON_INODE_INDIRECT) if indirect.i_block[j]]
                for j in range(POINTERS_ON_INODE_INDIRECT):
                    if not indirect.i_block[j]:
                        continue
                    double_indirect = Ext3InodeIndirect()
                    file_system.seek(indirect.i_block[j] * BLOCK_SIZE)
                    file_system.readinto(double_indirect)
                    # add [double_indirect.i_block[k] for k in range(POINTERS_ON_INODE_INDIRECT)]
                    used_blocks += [double_indirect.i_block[k] for k in range(POINTERS_ON_INODE_INDIRECT) if double_indirect.i_block[k]]
                    for k in range(POINTERS_ON_INODE_INDIRECT):
                        if not double_indirect.i_block[k]:
                            continue
                        triple_indirect = Ext3InodeIndirect()
                        file_system.seek(double_indirect.i_block[k] * BLOCK_SIZE)
                        file_system.readinto(triple_indirect)
                        # add [triple_indirect.i_block[l] for l in range(POINTERS_ON_INODE_INDIRECT)]
                        used_blocks += [triple_indirect.i_block[l] for l in range(POINTERS_ON_INODE_INDIRECT) if triple_indirect.i_block[l]]
            
            # now we just need to count the sequences on the used blocks
            n_segs = 0
            if n_used_blocks:
                n_segs = 1
                for _prev,_next in zip(used_blocks[:-1], used_blocks[1:]):
                    if _prev+1 != _next:
                        n_segs += 1
                    
                inode_segments_count += n_segs
            inode_segs.append(n_segs)
            if inode.i_mode & 0x8000: # regular file
                file_sizes.append(inode.i_size)
            
            #print(get_bit(entry_uint, i), hex(inode.i_mode),n_used_blocks,used_blocks, n_frags)
            #break # esse break aqui é para ser removido depois, é só para gerar apenas um arquivo por grupo, limitado a saida
            
            # com o inode lido é necessário percorrer o i-block para pegar o endereço dos blocos para verificar se eles são continuos
            # NOTA: o resultado disso aqui deve ser parecido com o do comando filefrag
            # filefrag -v nome do arquivo 
            # esse comando da a quantidade de fragmentaçoes e, com o parametro -v, mostra onde cada bloco do inode está

print("seg_contiguos_livres: %d" % block_free_segments_number)

frag_livres = (total_free_blocks * BLOCK_SIZE) / block_free_segments_number
print("frag_livres: %.2f KB/seg" % (frag_livres/1024)) # em KB/seg

frag_ocupados = (total_used_blocks * BLOCK_SIZE) / inode_segments_count
print("frag_ocupados: %.2f KB/seg" % (frag_ocupados/1024)) # em KB/seg

tx_frag_i_nodes = (inode_segments_count/total_used_inodes)
print("tx_frag_i_nodes: %.2f" % tx_frag_i_nodes)

def format_human(n_bytes):
    if n_bytes < 1024:
        return str(n_bytes)
    elif n_bytes < 1024 ** 2:
        return "%d KB" % (n_bytes >> 10)
    elif n_bytes < 1024 ** 3:
        return "%d MB" % (n_bytes >> 20)
    else:
        return "%d GB" % (n_bytes >> 30) 
def percent_under(f_size):
    return len([x for x in file_sizes if x<f_size])/len(file_sizes)
data = [(format_human(2**i), "%.4f%%" % (percent_under(2**i) * 100)) for i in range(0, 30)]
df = pd.DataFrame(data, columns = ["size", "everest"])
print(df.to_string(index=False))
