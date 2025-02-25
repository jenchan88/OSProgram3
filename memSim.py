# import sys

# TLB_SIZE = 16
# PAGE_TABLE_SIZE = 256
# PAGE_SIZE = 256
# FRAME_SIZE = 256

# class TLB:
#     def __init__(self):
#         self.entries = []  

#     def lookup(self, page_number):
#         # Search for the page num in TLB entries
#         for entry in self.entries:
#             if entry['page'] == page_number:
#                 return entry['frame']
#         return None 

#     def update(self, page_number, frame_number):
#         # FIFO pg replacement 
#         if len(self.entries) >= TLB_SIZE:
#             self.entries.pop(0)  
#         self.entries.append({'page': page_number, 'frame': frame_number})

# class PageTable:
#     def __init__(self):
#         self.entries = []  
#         for i in range(PAGE_TABLE_SIZE):  
#             self.entries.append({'frame': None, 'valid': False})  

#     def lookup(self, page_number):
#         if self.entries[page_number]['valid']:
#             return self.entries[page_number]['frame']
#         return None

#     def update(self, page_number, frame_number):
#         self.entries[page_number] = {'frame': frame_number, 'valid': True}

# class PhysicalMemory:
#     def __init__(self, num_frames):
#         self.frames = []
#         for i in range(num_frames):
#             self.frames.append(bytearray(FRAME_SIZE))
#         self.frame_queue = []
#         self.page_to_frame = {}
#         self.frame_to_page = {} 
#         self.current_pages = set()

#     def load_page(self, page_data, page_number):
#         if len(self.frames) == 0:
#             raise ValueError("No frames available in physical memory.")

#         if len(self.frame_queue) < len(self.frames):
#             frame_number = len(self.frame_queue)
#         else:
#             frame_number = self.frame_queue.pop(0)
#             old_page = self.frame_to_page.get(frame_number)
#             if old_page is not None:
#                 del self.page_to_frame[old_page]
#                 self.current_pages.remove(old_page)

#         self.frames[frame_number] = page_data
#         self.frame_queue.append(frame_number)
#         self.page_to_frame[page_number] = frame_number
#         self.frame_to_page[frame_number] = page_number  
#         self.current_pages.add(page_number)
#         print(f"Page {page_number} loaded into frame {frame_number}")
#         return frame_number

#     def is_page_in_memory(self, page_number):
#         return page_number in self.current_pages

#     def verify_page_loading(self, page_number, frame_number):
#         if self.page_to_frame.get(page_number) != frame_number:
#             print(f"Error: Page {page_number} is not in the expected frame {frame_number}")
#             return False
#         return True

# def read_backing_store(filename, page_number):
#     try:
#         with open(filename, 'rb') as f:
#             f.seek(page_number * PAGE_SIZE)
#             return f.read(PAGE_SIZE)
#     except FileNotFoundError:
#         print(f"Error: Backing store file '{filename}' not found.")
#         sys.exit(1)
#     except IOError as e:
#         print(f"Error reading from backing store file '{filename}': {e}")
#         sys.exit(1)
#     except Exception as e:
#         print(f"Unexpected error while reading backing store: {e}")
#         sys.exit(1)
    
# def simulate(addresses_file, num_frames):
#     tlb = TLB()
#     page_table = PageTable()
#     physical_memory = PhysicalMemory(num_frames)
    
#     page_faults = 0
#     tlb_hits = 0
#     total_references = 0

#     try:
#         with open(addresses_file, 'r') as f:
#             for line in f:
#                 try:
#                     logical_address = int(line.strip())
#                     page_number = (logical_address >> 8) & 0xFF
#                     offset = logical_address & 0xFF

#                     print(f"log address: {logical_address} (Page: {page_number}, Offset: {offset})")

#                     frame_number = tlb.lookup(page_number)
#                     if frame_number is not None:
#                         if physical_memory.is_page_in_memory(page_number):
#                             print(f"Hit: Page {page_number} is in frame {frame_number}")
#                             tlb_hits += 1
#                         else:
#                             print(f"TLB Soft Miss: Page {page_number} is in TLB but not in memory")
#                             frame_number = None  # Treat as a TLB miss
#                     else:
#                         print(f"Miss: Page {page_number} not found in TLB")

#                     if frame_number is None:
#                         frame_number = page_table.lookup(page_number)
#                         if frame_number is None or not physical_memory.is_page_in_memory(page_number):
#                             print(f"Page Fault: Page {page_number} not in memory")
#                             page_faults += 1
#                             try:
#                                 page_data = read_backing_store('BACKING_STORE.bin', page_number)
#                                 frame_number = physical_memory.load_page(page_data, page_number)
#                                 page_table.update(page_number, frame_number)
#                                 print(f"page loaded {page_number} into frame {frame_number}")
#                             except FileNotFoundError:
#                                 print("BACKING_STORE.bin not found.")
#                                 sys.exit(1)
#                             except IOError:
#                                 print("Error reading from BACKING_STORE.bin.")
#                                 sys.exit(1)
#                         else:
#                             print(f"Page {page_number} found in page table (Frame: {frame_number})")
#                         tlb.update(page_number, frame_number)
#                         print(f"TLB updated with page {page_number} -> frame {frame_number}")
#                         if not physical_memory.verify_page_loading(page_number, frame_number):
#                             print(f"Verification failed for page {page_number}")

#                     physical_address = (frame_number << 8) | offset
#                     unsigned_byte = physical_memory.frames[frame_number][offset]
#                     byte_value = unsigned_byte if unsigned_byte < 128 else unsigned_byte - 256

#                     frame_content = physical_memory.frames[frame_number].hex()
#                     print(f"Logical Address: {logical_address}, Byte Value: {byte_value}, Frame: {frame_number}")

#                     print(f"{logical_address},{byte_value},{frame_number},\n{frame_content}")
#                     total_references += 1

#                 except ValueError:
#                     print(f"Invalid address format in line: {line.strip()}")
#                     continue

#     except FileNotFoundError:
#         print(f"File {addresses_file} not found.")
#         sys.exit(1)
#     except IOError:
#         print(f"Error reading file {addresses_file}.")
#         sys.exit(1)

#     tlb_misses = total_references - tlb_hits
#     print(f"\nNumber of Translated Addresses = {total_references}")
#     print(f"Page Faults = {page_faults}")
#     print(f"Page Fault Rate = {page_faults/total_references:.3f}")
#     print(f"TLB Hits = {tlb_hits}")
#     print(f"TLB Misses = {tlb_misses}")
#     print(f"TLB Hit Rate = {tlb_hits/total_references:.3f}\n")



# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python memSim.py <reference-sequence-file.txt> [FRAMES]")
#         sys.exit(1)

#     addresses_file = sys.argv[1]
#     num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 256

#     simulate(addresses_file, num_frames)



# this section produces page nums for opt
# import sys

# TLB_SIZE = 16
# PAGE_TABLE_SIZE = 256
# PAGE_SIZE = 256
# FRAME_SIZE = 256

# class TLB:
#     def __init__(self):
#         self.entries = []  

#     def lookup(self, page_number):
#         for entry in self.entries:
#             if entry['page'] == page_number:
#                 return entry['frame']
#         return None 

#     def update(self, page_number, frame_number):
#         if len(self.entries) >= TLB_SIZE:
#             self.entries.pop(0)  
#         self.entries.append({'page': page_number, 'frame': frame_number})

# class PageTable:
#     def __init__(self):
#         self.entries = [{'frame': None, 'valid': False} for _ in range(PAGE_TABLE_SIZE)]  

#     def lookup(self, page_number):
#         if self.entries[page_number]['valid']:
#             return self.entries[page_number]['frame']
#         return None

#     def update(self, page_number, frame_number):
#         self.entries[page_number] = {'frame': frame_number, 'valid': True}

# class PhysicalMemory:
#     def __init__(self, num_frames, replacement_policy="FIFO", reference_list=None):
#         self.frames = [bytearray(FRAME_SIZE) for _ in range(num_frames)]
#         self.frame_queue = []
#         self.page_to_frame = {}
#         self.frame_to_page = {}
#         self.current_pages = set()
#         self.replacement_policy = replacement_policy
#         self.reference_list = reference_list if reference_list else []
#         self.reference_index = 0

#     def load_page(self, page_data, page_number):
#         if len(self.frames) == 0:
#             raise ValueError("No frames available in physical memory.")

#         if len(self.frame_queue) < len(self.frames):
#             frame_number = len(self.frame_queue)
#         else:
#             if self.replacement_policy == "FIFO":
#                 frame_number = self.frame_queue.pop(0)
#             elif self.replacement_policy == "OPT":
#                 frame_number = self.optimal_replace()
#             else:
#                 raise ValueError("Unsupported replacement policy.")

#             old_page = self.frame_to_page.get(frame_number)
#             if old_page is not None:
#                 del self.page_to_frame[old_page]
#                 self.current_pages.remove(old_page)

#         self.frames[frame_number] = page_data
#         self.frame_queue.append(frame_number)
#         self.page_to_frame[page_number] = frame_number
#         self.frame_to_page[frame_number] = page_number  
#         self.current_pages.add(page_number)
#         print(f"Page {page_number} loaded into frame {frame_number}")
#         return frame_number

#     def optimal_replace(self):
#         future_uses = {page: float('inf') for page in self.current_pages}

#         for index in range(self.reference_index, len(self.reference_list)):
#             future_page = self.reference_list[index]
#             if future_page in future_uses and future_uses[future_page] == float('inf'):
#                 future_uses[future_page] = index

#         page_to_replace = max(future_uses, key=future_uses.get)
#         frame_number = self.page_to_frame[page_to_replace]
        
#         print(f"OPT replacing page {page_to_replace} from frame {frame_number}")
#         return frame_number

#     def is_page_in_memory(self, page_number):
#         return page_number in self.current_pages

# def read_backing_store(filename, page_number):
#     try:
#         with open(filename, 'rb') as f:
#             f.seek(page_number * PAGE_SIZE)
#             return f.read(PAGE_SIZE)
#     except FileNotFoundError:
#         print(f"Error: Backing store file '{filename}' not found.")
#         sys.exit(1)
#     except IOError as e:
#         print(f"Error reading from backing store file '{filename}': {e}")
#         sys.exit(1)

# def get_reference_list(addresses_file):
#     reference_list = []
#     try:
#         with open(addresses_file, 'r') as f:
#             for line in f:
#                 try:
#                     logical_address = int(line.strip())
#                     page_number = (logical_address >> 8) & 0xFF
#                     reference_list.append(page_number)
#                 except ValueError:
#                     print(f"Invalid address format in line: {line.strip()}")
#     except FileNotFoundError:
#         print(f"File {addresses_file} not found.")
#         sys.exit(1)
#     return reference_list

# def simulate(addresses_file, num_frames, replacement_policy="FIFO"):
#     reference_list = get_reference_list(addresses_file)
#     tlb = TLB()
#     page_table = PageTable()
#     physical_memory = PhysicalMemory(num_frames, replacement_policy, reference_list)

#     page_faults = 0
#     tlb_hits = 0
#     total_references = 0

#     with open(addresses_file, 'r') as f:
#         for line in f:
#             try:
#                 logical_address = int(line.strip())
#                 page_number = (logical_address >> 8) & 0xFF
#                 offset = logical_address & 0xFF

#                 print(f"log address: {logical_address} (Page: {page_number}, Offset: {offset})")

#                 frame_number = tlb.lookup(page_number)
#                 if frame_number is not None:
#                     if physical_memory.is_page_in_memory(page_number):
#                         print(f"Hit: Page {page_number} is in frame {frame_number}")
#                         tlb_hits += 1
#                     else:
#                         print(f"TLB Soft Miss: Page {page_number} is in TLB but not in memory")
#                         frame_number = None  
#                 else:
#                     print(f"Miss: Page {page_number} not found in TLB")

#                 if frame_number is None:
#                     frame_number = page_table.lookup(page_number)
#                     if frame_number is None or not physical_memory.is_page_in_memory(page_number):
#                         print(f"Page Fault: Page {page_number} not in memory")
#                         page_faults += 1
#                         page_data = read_backing_store('BACKING_STORE.bin', page_number)
#                         frame_number = physical_memory.load_page(page_data, page_number)
#                         page_table.update(page_number, frame_number)
#                     else:
#                         print(f"Page {page_number} found in page table (Frame: {frame_number})")

#                     tlb.update(page_number, frame_number)

#                 physical_address = (frame_number << 8) | offset
#                 byte_value = physical_memory.frames[frame_number][offset]
#                 print(f"Logical Address: {logical_address}, Byte Value: {byte_value}, Frame: {frame_number}")

#                 total_references += 1
#                 physical_memory.reference_index += 1

#             except ValueError:
#                 print(f"Invalid address format in line: {line.strip()}")
#                 continue

#     print(f"\nNumber of Translated Addresses = {total_references}")
#     print(f"Page Faults = {page_faults}")
#     print(f"Page Fault Rate = {page_faults/total_references:.3f}")
#     print(f"TLB Hits = {tlb_hits}")
#     print(f"TLB Hit Rate = {tlb_hits/total_references:.3f}\n")

# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python memSim.py <reference-sequence-file.txt> <FRAMES> [FIFO|OPT]")
#         sys.exit(1)

#     addresses_file = sys.argv[1]
#     num_frames = int(sys.argv[2])
#     replacement_policy = sys.argv[3].upper() if len(sys.argv) > 3 else "FIFO"

#     simulate(addresses_file, num_frames, replacement_policy)

import sys

TLB_SIZE = 16
PAGE_TABLE_SIZE = 65536
PAGE_SIZE = 256
FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.entries = []

    def lookup(self, page_number):
        for entry in self.entries:
            if entry['page'] == page_number:
                return entry['frame']
        return None

    def update(self, page_number, frame_number):
        if len(self.entries) >= TLB_SIZE:
            self.entries.pop(0)
        self.entries.append({'page': page_number, 'frame': frame_number})

class PageTable:
    def __init__(self):
        self.entries = [{'frame': None, 'valid': False} for _ in range(PAGE_TABLE_SIZE)]

    def lookup(self, page_number):
        if self.entries[page_number]['valid']:
            return self.entries[page_number]['frame']
        return None

    def update(self, page_number, frame_number):
        self.entries[page_number] = {'frame': frame_number, 'valid': True}

class PhysicalMemory:
    def __init__(self, num_frames, algorithm='FIFO'):
        self.frames = [bytearray(FRAME_SIZE) for _ in range(num_frames)]
        self.frame_queue = []
        self.page_to_frame = {}
        self.frame_to_page = {}
        self.current_pages = set()
        self.algorithm = algorithm
        self.future_accesses = None

    def load_page(self, page_data, page_number):
        if len(self.frames) > len(self.page_to_frame):
            frame_number = len(self.page_to_frame)
        else:
            frame_number = self.replace_page(page_number)

        self.frames[frame_number] = page_data
        if self.algorithm == 'FIFO':
            self.frame_queue.append(frame_number)
        self.page_to_frame[page_number] = frame_number
        self.frame_to_page[frame_number] = page_number
        self.current_pages.add(page_number)
        print(f"Page {page_number} loaded into frame {frame_number}")
        return frame_number

    def replace_page(self, new_page):
        if self.algorithm == 'FIFO':
            frame_number = self.frame_queue.pop(0)
        elif self.algorithm == 'OPT':
            frame_number = self.get_optimal_replacement(new_page)
        
        old_page = self.frame_to_page[frame_number]
        del self.page_to_frame[old_page]
        self.current_pages.remove(old_page)
        return frame_number

    def get_optimal_replacement(self, new_page):
        farthest_use = -1
        frame_to_replace = None

        for frame, page in self.frame_to_page.items():
            if page not in self.future_accesses:
                return frame
            next_use = self.future_accesses.index(page)
            if next_use > farthest_use:
                farthest_use = next_use
                frame_to_replace = frame

        return frame_to_replace

    def is_page_in_memory(self, page_number):
        return page_number in self.current_pages

    def set_future_accesses(self, future_accesses):
        self.future_accesses = future_accesses

def read_backing_store(filename, page_number):
    try:
        with open(filename, 'rb') as f:
            f.seek(page_number * PAGE_SIZE)
            return f.read(PAGE_SIZE)
    except FileNotFoundError:
        print(f"Error: Backing store file '{filename}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading from backing store file '{filename}': {e}")
        sys.exit(1)

def simulate(addresses_file, num_frames, algorithm):
    tlb = TLB()
    page_table = PageTable()
    physical_memory = PhysicalMemory(num_frames, algorithm)
    
    page_faults = 0
    tlb_hits = 0
    total_references = 0

    try:
        with open(addresses_file, 'r') as f:
            addresses = [int(line.strip()) for line in f]
    except FileNotFoundError:
        print(f"Error: Addresses file '{addresses_file}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading addresses file '{addresses_file}': {e}")
        sys.exit(1)

    if algorithm == 'OPT':
        future_pages = [(addr >> 8) & 0xFF for addr in addresses]
        physical_memory.set_future_accesses(future_pages)

    for logical_address in addresses:
        page_number = (logical_address >> 8) & 0xFF
        offset = logical_address & 0xFF

        frame_number = tlb.lookup(page_number)
        if frame_number is not None:
            tlb_hits += 1
        else:
            frame_number = page_table.lookup(page_number)
            if frame_number is None or not physical_memory.is_page_in_memory(page_number):
                page_faults += 1
                page_data = read_backing_store('BACKING_STORE.bin', page_number)
                frame_number = physical_memory.load_page(page_data, page_number)
                page_table.update(page_number, frame_number)
            tlb.update(page_number, frame_number)

        physical_address = (frame_number << 8) | offset
        byte_value = physical_memory.frames[frame_number][offset]
        if byte_value > 127:
            byte_value -= 256

        frame_content = physical_memory.frames[frame_number].hex()
        print(f"{logical_address},{byte_value},{frame_number},\n{frame_content}")
        
        total_references += 1
        if algorithm == 'OPT':
            physical_memory.future_accesses.pop(0)

    tlb_misses = total_references - tlb_hits
    print(f"\nNumber of Translated Addresses = {total_references}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {page_faults/total_references:.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {tlb_hits/total_references:.3f}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python memSim.py <reference-sequence-file.txt> <FRAMES> [<PRA>]")
        sys.exit(1)

    addresses_file = sys.argv[1]
    num_frames = int(sys.argv[2])
    algorithm = sys.argv[3] if len(sys.argv) > 3 else 'FIFO'

    simulate(addresses_file, num_frames, algorithm)
