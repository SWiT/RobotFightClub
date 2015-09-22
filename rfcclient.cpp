#include <string.h>
#include <cstring>
#include <unistd.h>
#include <stdio.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <strings.h>
#include <stdlib.h>
#include <string>
#include <time.h>
#include <vector>
using namespace std;

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
    
    //char recvbuff[301];
    //bzero(recvbuff, 301);
    
    // Main loop.
    for(;;)
    {
        /*bzero(recvbuff, 301);
        recv(conn, recvbuff, 300, 0);
        string recvstr (recvbuff);
        if (recvstr != ""){
            cout << recvstr << endl;
        }
        */
        char s[301];
        bzero(s, 301);
        cout << "Enter stuff: ";
        cin.getline(s, 300);
        
        //char s[] = "hello?\0";
        send(conn, s, strlen(s), 0);
        
        string cmdstr (s);
        if (cmdstr == "disconnect"){
            break;
        }
        
    }
    close(conn);
    cout << "Exiting." << endl;
}
