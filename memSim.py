import sys

TLB_SIZE = 16
PAGE_TABLE_SIZE = 256
PAGE_SIZE = 256
FRAME_SIZE = 256

class TLB:
    def __init__(self):
        self.entries = []  

    def lookup(self, page_number):
        # Search for the page num in TLB entries
        for entry in self.entries:
            if entry['page'] == page_number:
                return entry['frame']
        return None 

    def update(self, page_number, frame_number):
        # FIFO pg replacement 
        if len(self.entries) >= TLB_SIZE:
            self.entries.pop(0)  
        self.entries.append({'page': page_number, 'frame': frame_number})

class PageTable:
    def __init__(self):
        self.entries = []  
        for i in range(PAGE_TABLE_SIZE):  
            self.entries.append({'frame': None, 'valid': False})  

    def lookup(self, page_number):
        if self.entries[page_number]['valid']:
            return self.entries[page_number]['frame']
        return None

    def update(self, page_number, frame_number):
        self.entries[page_number] = {'frame': frame_number, 'valid': True}

class PhysicalMemory:
    def __init__(self, num_frames):
        self.frames = []
        for i in range(num_frames):
            self.frames.append(bytearray(FRAME_SIZE))
        self.frame_queue = []
        self.page_to_frame = {}

    def load_page(self, page_data, page_number):
        # FIFO pg replacement
        if len(self.frame_queue) < len(self.frames):
            frame_number = len(self.frame_queue)
        else:
            frame_number = self.frame_queue.pop(0)  
            old_page = next(page for page, frame in self.page_to_frame.items() if frame == frame_number)
            del self.page_to_frame[old_page]

        self.frames[frame_number] = page_data
        self.frame_queue.append(frame_number)
        self.page_to_frame[page_number] = frame_number
        print(f"Page {page_number} loaded into frame {frame_number}")
        return frame_number
    
    def verify_page_loading(self, page_number, frame_number):
        if self.page_to_frame.get(page_number) != frame_number:
            print(f"Error: Page {page_number} is not in the expected frame {frame_number}")
            return False
        return True

def read_backing_store(filename, page_number):
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

    try:
        with open(addresses_file, 'r') as f:
            for line in f:
                try:
                    logical_address = int(line.strip())
                    page_number = (logical_address >> 8) & 0xFF
                    offset = logical_address & 0xFF

                    frame_number = tlb.lookup(page_number)
                    if frame_number is not None:
                        tlb_hits += 1
                    else:
                        frame_number = page_table.lookup(page_number)
                        if frame_number is None:
                            page_faults += 1
                            try:
                                page_data = read_backing_store('BACKING_STORE.bin', page_number)
                                frame_number = physical_memory.load_page(page_data, page_number)
                                page_table.update(page_number, frame_number)
                            except FileNotFoundError:
                                print("BACKING_STORE.bin not found.")
                                sys.exit(1)
                            except IOError:
                                print("Error reading from BACKING_STORE.bin.")
                                sys.exit(1)
                        tlb.update(page_number, frame_number)
                        if not physical_memory.verify_page_loading(page_number, frame_number):
                            print(f"Verification failed for page {page_number}")

                    physical_address = (frame_number << 8) | offset
                    unsigned_byte = physical_memory.frames[frame_number][offset]
                    byte_value = unsigned_byte if unsigned_byte < 128 else unsigned_byte - 256

                    frame_content = physical_memory.frames[frame_number].hex()

                    print(f"{logical_address},{byte_value},{frame_number},\n{frame_content}")
                    total_references += 1

                except ValueError:
                    print(f"Invalid address format in line: {line.strip()}")
                    continue

    except FileNotFoundError:
        print(f"File {addresses_file} not found.")
        sys.exit(1)
    except IOError:
        print(f"Error reading file {addresses_file}.")
        sys.exit(1)

    tlb_misses = total_references - tlb_hits
    print(f"\nNumber of Translated Addresses = {total_references}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {page_faults/total_references:.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {tlb_hits/total_references:.3f}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python memSim.py <reference-sequence-file.txt> [FRAMES]")
        sys.exit(1)

    addresses_file = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 256

    simulate(addresses_file, num_frames)
