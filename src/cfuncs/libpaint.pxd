from libc.stdint cimport uint32_t 

cdef extern from "c_src/libpaint.c":
    int width, height
    void resize(int w, int h)
    bint in_borders(int x, int y)
    void floodFill(uint32_t *data, uint32_t n_color, uint32_t color, int x, int y)
    void draw(uint32_t *data, int radius, int x, int y, int mx, int my, uint32_t color)

