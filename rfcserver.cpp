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

void *clientThread(void *);

static int conn;

int numThreads = 0;

int main(int argc, char* argv[])
{
    int portNum, sockListen;
    socklen_t socklen;
    struct sockaddr_in svrAdd, clntAdd;
    
    pthread_t threadid[RFC_MAX_CLIENTS];
    
    if (argc < 2)
    {
        cerr << "Syntam : ./server <port>" << endl;
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
    cout << "RFC Server listening on port " << portNum << endl;
    cout << numThreads << " Threads" << endl;
    for(;;)
    {
        socklen = sizeof(clntAdd);

        conn = accept(sockListen, (struct sockaddr *)&clntAdd, &socklen);
        if (conn >= 0)
        {
            cout << "Connection successful" << endl;
            pthread_create(&threadid[numThreads], NULL, clientThread, NULL); 
            numThreads++;
            cout << numThreads << " Threads" << endl;
        }
    }
    
    cout << "\nRFC Server Exiting." << endl;
    return 1;
}

void *clientThread (void *param)
{
    cout << "Thread Number: " << pthread_self() << endl;
    char buff[301];
    bzero(buff, 301);
    for(;;)
    {    
        bzero(buff, 301);
        
        recv(conn, buff, 300, 0);
        
        string cmdstr (buff);
        
        if (cmdstr != ""){
            cout << cmdstr << endl;
        }
        if(cmdstr == "exit")
            break;
            
    }
    cout << "Closing thread "  << pthread_self() << endl;
    close(conn);
}



