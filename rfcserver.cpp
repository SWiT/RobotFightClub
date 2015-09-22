#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <fstream>
#include <strings.h>
#include <stdlib.h>
#include <string>
#include <pthread.h>

//#include <fcntl.h>

using namespace std;

#define RFC_MAX_CLIENTS 6
#define BUFFERSIZE 256

void *clientThread(void *);

static int conn;

int main(int argc, char* argv[])
{
    int portNum, sockListen;
    socklen_t socklen;
    struct sockaddr_in svrAdd, clntAdd;
    
    pthread_t threadid[RFC_MAX_CLIENTS];
    
    if (argc < 2)
    {
        cerr << "Syntax : ./server <port>" << endl;
        return 0;
    }
    
    portNum = atoi(argv[1]);
    
    if((portNum > 65535) || (portNum < 2000))
    {
        cerr << "Please enter a port number between 2000 - 65535" << endl;
        return 0;
    }
    
    //create socket
    sockListen = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(sockListen < 0)
    {
        cerr << "Cannot open socket" << endl;
        return 0;
    }
    //fcntl(sockListen, F_SETFL, O_NONBLOCK);  // set to non-blocking
    
    bzero((char*) &svrAdd, sizeof(svrAdd));
    
    svrAdd.sin_family = AF_INET;
    svrAdd.sin_addr.s_addr = INADDR_ANY;
    svrAdd.sin_port = htons(portNum);
    
    //bind socket
    if(bind(sockListen, (struct sockaddr *)&svrAdd, sizeof(svrAdd)) < 0)
    {
        cerr << "Cannot bind" << endl;
        return 0;
    }
    
    listen(sockListen, RFC_MAX_CLIENTS);
    cout << "\nRFC Server listening on port " << portNum << endl;
    
    int threadIndex = 0;
    
    // Main loop.
    for(;;)
    {
        socklen = sizeof(clntAdd);
        conn = accept(sockListen, (struct sockaddr *)&clntAdd, &socklen);
        if (conn >= 0)
        {
            cout << "Connection successful" << endl;
            pthread_create(&threadid[threadIndex], NULL, clientThread, NULL); 
        }
    }
    return 1;
}

// Client Thread.
void *clientThread (void *param)
{
    cout << "Starting thread " << pthread_self() << endl;
    char recvbuff[BUFFERSIZE];
    bzero(recvbuff, BUFFERSIZE);
    
    int bytessent = 0;
    int bytesrecv = 0;
    
    for(;;)
    {    
        char s[] = "{for the client};";
        bytessent = send(conn, s, strlen(s), 0);
        if (bytessent > 0)
        {
            cout << "Sent: " << bytessent << endl;
        }
    
        bzero(recvbuff, BUFFERSIZE);
        bytesrecv = recv(conn, recvbuff, BUFFERSIZE-1, 0);
        if(bytesrecv > 0)
        {
            cout << "Recv: " << bytesrecv << endl;
            recvbuff[bytesrecv] = '\0';
            string recvstr (recvbuff);
            if (recvstr != "")
            {
                cout << recvstr << " ... " << endl;
            }
        }
        
    }
    cout << "Closing thread "  << pthread_self() << endl;
    close(conn);
}



