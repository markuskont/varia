#include <stdio.h>

void parse_file (const char *filename)
{
	FILE *file = fopen( filename, "r" );

	if ( file == 0 )
	{
		printf( "Unable to open file\n" );
	}
	else
	{
		int x;
		while (( x = fgetc (file)) != EOF )
		{
			printf( "%c", x );
		}
		fclose( file );
	}
}

int main(int argc, char *argv[])
{
	if (argc != 2)
	{
		printf( "usage: %s <filename> \n", argv[0] );
	}
	else
	{
		parse_file(argv[1]);
	}
	return 0;
}
