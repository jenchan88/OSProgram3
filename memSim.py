import sys

# Constants
TLB_SIZE = 16
PAGE_TABLE_SIZE = 256
PAGE_SIZE = 256
FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.entries = []  # List to store TLB entries

    def lookup(self, page_number):
        # Search for the page number in TLB entries
        for entry in self.entries:
            if entry['page'] == page_number:
                return entry['frame']
        return None  # Return None if not found

    def update(self, page_number, frame_number):
        # Implement FIFO replacement for TLB
        if len(self.entries) >= TLB_SIZE:
            self.entries.pop(0)  # Remove oldest entry
        self.entries.append({'page': page_number, 'frame': frame_number})

class PageTable:
    def __init__(self):
        self.entries = []  
        for i in range(PAGE_TABLE_SIZE):  
            self.entries.append({'frame': None, 'valid': False})  

    def lookup(self, page_number):
        # Check if the page is valid and return its frame number
        if self.entries[page_number]['valid']:
            return self.entries[page_number]['frame']
        return None

    def update(self, page_number, frame_number):
        # Update the page table entry
        self.entries[page_number] = {'frame': frame_number, 'valid': True}

class PhysicalMemory:
    def __init__(self, num_frames):
        # Initialize physical memory with the specified number of frames
        self.frames = [bytearray(FRAME_SIZE) for _ in range(num_frames)]
        self.frame_queue = []  # Queue for FIFO replacement

    def load_page(self, page_data):
        # Implement FIFO page replacement
        if len(self.frame_queue) < len(self.frames):
            frame_number = len(self.frame_queue)
        else:
            frame_number = self.frame_queue.pop(0)  # Remove oldest frame
        self.frames[frame_number] = page_data
        self.frame_queue.append(frame_number)
        return frame_number

def read_backing_store(filename, page_number):
    # Read a page from the backing store file
    with open(filename, 'rb') as f:
        f.seek(page_number * PAGE_SIZE)
        return f.read(PAGE_SIZE)

def simulate(addresses_file, num_frames):
    tlb = TLB()
    page_table = PageTable()
    physical_memory = PhysicalMemory(num_frames)
    
    page_faults = 0
    tlb_hits = 0
    total_references = 0

    # TODO: Add error handling for file opening
    with open(addresses_file, 'r') as f:
        for line in f:
            logical_address = int(line.strip())
            # Extract page number and offset from logical address
            page_number = (logical_address >> 8) & 0xFF
            offset = logical_address & 0xFF

            # Look up in TLB
            frame_number = tlb.lookup(page_number)
            if frame_number is not None:
                tlb_hits += 1
            else:
                # TLB miss, look up in page table
                frame_number = page_table.lookup(page_number)
                if frame_number is None:
                    # Page fault
                    page_faults += 1
                    page_data = read_backing_store('BACKING_STORE.bin', page_number)
                    frame_number = physical_memory.load_page(page_data)
                    page_table.update(page_number, frame_number)
                tlb.update(page_number, frame_number)

            physical_address = (frame_number << 8) | offset
            # byte_value = physical_memory.frames[frame_number][offset]
            unsigned_byte = physical_memory.frames[frame_number][offset]
            byte_value = unsigned_byte if unsigned_byte < 128 else unsigned_byte - 256

            # frame_content = ''.join(f'{b:02x}' for b in physical_memory.frames[frame_number])
            frame_content = physical_memory.frames[frame_number].hex()


            print(f"{logical_address},{byte_value},{frame_number},\n{frame_content}")
            total_references += 1

    # Print statistics
    tlb_misses = total_references - tlb_hits
    
    print(f"\nNumber of Translated Addresses = {total_references}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {page_faults/total_references:.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {tlb_hits/total_references:.3f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python memSim.py <reference-sequence-file.txt> [FRAMES]")
        sys.exit(1)

    addresses_file = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 256

    simulate(addresses_file, num_frames)
