#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#include "queue.h"

//Dimensions//
int width, height, length;

//Adjusting dimensions//
void resize(int w, int h){
    width = w;
    height= h;
    length= w*h;
}

bool in_borders(int x, int y){return x >=0 && x < width && y >= 0 && y < height;}

//Bresenham's circle prototype function//
void circle(uint32_t *, int, int, int, int);

//d_color variable to check if call circle() function or not//
void lineFrom(uint32_t *data, int radius, int x, int y, int mx, int my, int color, bool d_circle){
    int dx = x-mx;
    int dy = y-my;

    if(!dx && !dy) return; //Check movements
    
    //Borders adjustement
    if(in_borders(mx, my)){
        if(!in_borders(x, 0)){
            if(x > width/2) x=width-1;
            if(x < width/2) x=0;
        }

        if(!in_borders(0, y)){
            if(y > height/2) y=height-1;
            if(y < height/2) y=0;
        }
    }

    if(!in_borders(x, y)) return;
    int adx, ady, cy, cx;
    adx = abs(dx); ady = abs(dy);
    data[y*width+x] = color;
    
    for(int i=0; i < adx; i++){
        cy = my+(int)(dy*(i/(double)adx));
        cx = mx + i;
        if(dx < 0) cx = mx-i;
        if(in_borders(cx, cy)){ 
            data[cy*width+cx] = color;
            if(d_circle && radius > 0) circle(data, cx, cy, radius, color);
        }
    }

    for(int j=0; j < ady; j++){
        cx = mx+(int)(dx*(j/(double)ady));
        cy = my + j;
        if(dy < 0) cy = my - j;
        if(in_borders(cx, cy)){
            data[cy*width+cx] = color;
            if(d_circle && radius > 0) circle(data, cx, cy, radius, color);
        }
    }

}

void circle(uint32_t *data, int cx, int cy, int r, int color){
    int x = 0;
    int y = r;
    int d = 3-(2*r);
    data[cy*width+cx] = 0;

    while(y >= x){

        //8 root points for drawing circle//
        lineFrom(data, r, cx, cy, cx+x, cy+y, color, false);
        lineFrom(data, r, cx, cy, cx-x, cy+y, color, false);
        lineFrom(data, r, cx, cy, cx+x, cy-y, color, false);
        lineFrom(data, r, cx, cy, cx-x, cy-y, color, false);
        lineFrom(data, r, cx, cy, cx+y, cy+x, color, false);
        lineFrom(data, r, cx, cy, cx-y, cy+x, color, false);
        lineFrom(data, r, cx, cy, cx+y, cy-x, color, false);
        lineFrom(data, r, cx, cy, cx-y, cy-x, color, false);

        if(d > 0){
            d = d + (4 * (x - y)) + 10;
            y--;
        }
        else
            d = d + 4 * x + 6;
        x++;
    }
}

//Drawing initializing function//
void draw(uint32_t* data, int radius, int x, int y, int mx, int my, uint32_t color){
    lineFrom(data, radius, x, y, mx, my, color, true);
}

//Fills//
void floodFill(uint32_t *data, uint32_t n_color, uint32_t c_color, int x, int y){
	queue_t dqueue; // View more in "queue.h"
   	bool visited[length]; //Visited points
	
	//Array & queue initialization
	for(int i = 0; i < length; i++) visited[i] = false;
	QUEUE_INITIALIZE(&dqueue, width);
	QUEUE_ENQUEUE(&dqueue, x, y);
	
	int point;
	while((point = QUEUE_DEQUEUE(&dqueue, &x, &y)) != QUEUE_EMPTY){
		
		if(in_borders(x, y) && !visited[point] && data[point] == c_color){
			visited[point] = true;
			data[point] = n_color;
			
			QUEUE_ENQUEUE(&dqueue, x-1, y);
			QUEUE_ENQUEUE(&dqueue, x+1, y);
			QUEUE_ENQUEUE(&dqueue, x, y+1);
			QUEUE_ENQUEUE(&dqueue, x, y-1);
		}
	}
}
