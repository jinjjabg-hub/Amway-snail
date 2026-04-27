import struct, zlib

def make_png(size):
    w, h = size, size
    margin = size // 9
    bg = (0x1D, 0x9E, 0x75, 255)
    transparent = (0, 0, 0, 0)
    pixels = [[list(bg) for _ in range(w)] for _ in range(h)]

    def setpx(x, y, col):
        if 0 <= x < w and 0 <= y < h:
            pixels[y][x] = list(col)

    def fill_circle(cx, cy, r, col):
        for y2 in range(max(0, int(cy-r)-1), min(h, int(cy+r)+2)):
            for x2 in range(max(0, int(cx-r)-1), min(w, int(cx+r)+2)):
                if (x2-cx)**2 + (y2-cy)**2 <= r*r:
                    setpx(x2, y2, col)

    def fill_ellipse(cx, cy, rx, ry, col):
        rxf = max(rx, 0.1)
        ryf = max(ry, 0.1)
        for y2 in range(max(0, int(cy-ry)-1), min(h, int(cy+ry)+2)):
            for x2 in range(max(0, int(cx-rx)-1), min(w, int(cx+rx)+2)):
                if ((x2-cx)/rxf)**2 + ((y2-cy)/ryf)**2 <= 1:
                    setpx(x2, y2, col)

    def draw_line(x1, y1, x2, y2, col, th=1):
        dx, dy = x2-x1, y2-y1
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps+1):
            x = int(x1 + dx*i/steps)
            y = int(y1 + dy*i/steps)
            for tx in range(-th, th+1):
                for ty in range(-th, th+1):
                    setpx(x+tx, y+ty, col)

    s = size / 192.0

    # Rounded corners
    for y in range(h):
        for x in range(w):
            cx2, cy2 = None, None
            if x < margin and y < margin:
                cx2, cy2 = margin, margin
            elif x >= w-margin and y < margin:
                cx2, cy2 = w-margin-1, margin
            elif x < margin and y >= h-margin:
                cx2, cy2 = margin, h-margin-1
            elif x >= w-margin and y >= h-margin:
                cx2, cy2 = w-margin-1, h-margin-1
            if cx2 is not None and (x-cx2)**2 + (y-cy2)**2 > margin*margin:
                pixels[y][x] = list(transparent)

    body = (255, 255, 204, 255)
    sh1  = (153, 60, 29, 255)
    sh2  = (240, 153, 123, 255)
    sh3  = (250, 236, 231, 255)
    eye  = (34, 34, 34, 255)
    wh   = (255, 255, 255, 255)

    fill_ellipse(int(96*s), int(130*s), int(62*s), int(26*s), body)
    fill_ellipse(int(150*s), int(138*s), int(16*s), int(11*s), body)
    fill_circle(int(44*s), int(128*s), int(19*s), body)
    fill_circle(int(88*s), int(100*s), int(50*s), sh1)
    fill_circle(int(88*s), int(100*s), int(40*s), sh2)
    fill_circle(int(88*s), int(100*s), int(28*s), sh3)
    fill_circle(int(88*s), int(100*s), int(16*s), sh2)
    fill_circle(int(88*s), int(100*s), int(7*s),  sh1)
    th = max(1, int(2*s))
    draw_line(int(40*s), int(114*s), int(30*s), int(80*s), body, th)
    draw_line(int(48*s), int(113*s), int(58*s), int(80*s), body, th)
    fill_circle(int(29*s), int(77*s), int(5*s), eye)
    fill_circle(int(59*s), int(77*s), int(5*s), eye)
    fill_circle(int(28*s), int(75*s), int(2*s), wh)
    fill_circle(int(58*s), int(75*s), int(2*s), wh)

    raw = b''
    for row in pixels:
        raw += b'\x00'
        for px in row:
            raw += bytes(px)

    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

    ihdr = struct.pack('>II', w, h) + bytes([8, 6, 0, 0, 0])
    png  = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw, 6))
    png += chunk(b'IEND', b'')
    return png

for sz in [192, 512]:
    fname = 'icons/icon-' + str(sz) + '.png'
    with open(fname, 'wb') as f:
        f.write(make_png(sz))
    print(fname + ' OK')
