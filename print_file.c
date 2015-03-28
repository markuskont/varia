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
		/* buffer size from syslog RFC5426 */
		char line [480];

		while ( fgets ( line, sizeof line, file ) != NULL ) /* read a line */
		{
			fputs ( line, stdout ); /* write the line */
		}
		fclose ( file );
	}
}

int main(int argc, char *argv[])
{
	if (argc != 2)
	{
		printf( "Usage: %s <filename> \n", argv[0] );
	}
	else
	{
		parse_file(argv[1]);
	}
	return 0;
}
