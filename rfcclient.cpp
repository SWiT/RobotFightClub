#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <iostream>
#include <stdlib.h>

using namespace std;

#define BUFFERSIZE 256

int main (int argc, char* argv[])
{
    int conn, portNo;
    bool loop = false;
    struct sockaddr_in svrAdd;
    struct hostent *server;
    
    if(argc < 3)
    {
        cerr<<"Syntax : ./client <host name> <port>"<<endl;
        return 0;
    }
    
    portNo = atoi(argv[2]);
    if((portNo > 65535) || (portNo < 2000))
    {
        cerr<<"Please enter port number between 2000 - 65535"<<endl;
        return 0;
    }       
    
    // Create socket connection.
    conn = socket(AF_INET, SOCK_STREAM, 0);
    if(conn < 0)
    {
        cerr << "Cannot open socket" << endl;
        return 0;
    }
    
    server = gethostbyname(argv[1]);
    if(server == NULL)
    {
        cerr << "Host does not exist" << endl;
        return 0;
    }
    
    bzero((char *) &svrAdd, sizeof(svrAdd));
    svrAdd.sin_family = AF_INET;
    bcopy((char *) server -> h_addr, (char *) &svrAdd.sin_addr.s_addr, server -> h_length);
    svrAdd.sin_port = htons(portNo);
    
    int checker = connect(conn,(struct sockaddr *) &svrAdd, sizeof(svrAdd));
    if (checker < 0)
    {
        cerr << "Cannot connect!" << endl;
        return 0;
    }
    
    char recvbuff[BUFFERSIZE];
    bzero(recvbuff, BUFFERSIZE);
    
    int bytessent = 0;
    int bytesrecv = 0;
    
    // Main loop.
    for(;;)
    {
        char s[] = "{for the server};";
        bytessent = send(conn, s, strlen(s), 0);
        if (bytessent > 0)
        {
            cout << "Sent: " << bytessent << endl;
        }
        
        bzero(recvbuff, BUFFERSIZE);
        bytesrecv = recv(conn, recvbuff, BUFFERSIZE-1, 0);
        if (bytesrecv > 0)
        {
            cout << "Recv: " << bytesrecv << endl;
            recvbuff[bytesrecv] = '\0';
            cout << recvbuff << " ... " << endl;
        }
    }
    close(conn);
    cout << "Exiting." << endl;
}
