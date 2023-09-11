#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc_c.h"

#include <ctype.h>
#include <stdio.h>

int main( int argc, char** argv )
{
    CvCapture* capture = 0;
    IplImage*  log_polar_img = 0;
    char *filename;

    //if( argc == 1 || (argc == 2 && strlen(argv[1]) == 1 && isdigit(argv[1][0])))
        //capture = cvCaptureFromCAM( argc == 2 ? argv[1][0] - '0' : 0 );
    printf("%d %s",argc,argv[1]);
    if (argc !=2) {
	printf("Dame\n");
        return 1;
    }

    capture = cvCaptureFromCAM(0);

    IplImage* frame = 0;
    frame = cvQueryFrame( capture );
    filename=argv[1];
    //cvSaveImage("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large.jpg",frame,0);
    cvSaveImage(filename,frame,0);

    return 0;
}

#ifdef _EiC
main(1,"laplace.c");
#endif
