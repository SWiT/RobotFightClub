#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <iostream>
#include <stdlib.h>
#include <pthread.h>
#include <stack>

using namespace std;

#define RFC_MAX_CLIENTS 6
#define BUFFERSIZE 256

void *clientThread(void *);

static int conn[RFC_MAX_CLIENTS];

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
        conn[threadIndex] = accept(sockListen, (struct sockaddr *)&clntAdd, &socklen);
        if (conn[threadIndex] >= 0)
        {
            cout << "Connection successful" << endl;
            
            int arg = threadIndex;
            
            
            pthread_create(&threadid[threadIndex], NULL, clientThread, (void *) arg); 
            threadIndex++;
            if (threadIndex >= RFC_MAX_CLIENTS) {
                threadIndex = 0;
            }
        }
    }
    return 1;
}

// Client Thread.
void *clientThread (void *param)
{
    int idx = *((int *) param);
    //idx = (int *) param;

    cout << "Starting thread " << pthread_self() << " : " << idx << endl;
    char recvbuff[BUFFERSIZE];
    bzero(recvbuff, BUFFERSIZE);
    
    char sendbuff[BUFFERSIZE];
    bzero(sendbuff, BUFFERSIZE);
    
    int bytessent = 0;
    int bytesrecv = 0;
    
    for(;;)
    {    
        strcpy(sendbuff, "{for the client};");
        //bytessent = send(conn[idx], sendbuff, strlen(sendbuff), 0);
        if (bytessent > 0)
        {
            cout << "Sent: " << bytessent << endl;
        }
    
        bzero(recvbuff, BUFFERSIZE);
        //bytesrecv = recv(conn[idx], recvbuff, BUFFERSIZE-1, 0);
        if(bytesrecv > 0)
        {
            cout << "Recv: " << bytesrecv << endl;
            recvbuff[bytesrecv] = '\0';
            cout << recvbuff << " ... " << endl;
        }
        
    }
    cout << "Closing thread "  << pthread_self() << endl;
    //close(conn[idx]);
}



