YUI().use('node', 'event', 'io-base', function (Y) {
    
    var sockethost = Y.one("#socketiohost").get('value');
    var socket = io.connect('http://'+sockethost);
    
    socket.on('robotstatus', function (data) {
        console.log(data);
    });
    
    var doc = Y.one(Y.config.doc);
    
    doc.on('keydown', function(e){
        if(e.keyCode == 37){        //left-arrow
            Y.one('#arrow-left').setStyle('borderRightColor','#000000');
            socket.emit('drive', { key:'left-arrow', status:'down'});
            
        }else if(e.keyCode == 38){  //up-arrow
            Y.one('#arrow-up').setStyle('borderBottomColor','#000000');
            socket.emit('drive', { key:'up-arrow', status:'down'});
            
        }else if(e.keyCode == 39){  //right-arrow
            Y.one('#arrow-right').setStyle('borderLeftColor','#000000');
            socket.emit('drive', { key:'right-arrow', status:'down'});
            
        }else if(e.keyCode == 40){  //down-arrow
            Y.one('#arrow-down').setStyle('borderTopColor','#000000');
            socket.emit('drive', { key:'down-arrow', status:'down'});
        }
    });
    
    doc.on('keyup', function(e){
        if(e.keyCode == 37){
            Y.one('#arrow-left').setStyle('borderRightColor','#bbbbbb');
            socket.emit('drive', { key:'left-arrow', status:'up'});
            
        }else if(e.keyCode == 38){
            Y.one('#arrow-up').setStyle('borderBottomColor','#bbbbbb');
            socket.emit('drive', { key:'up-arrow', status:'up'});
            
        }else if(e.keyCode == 39){
            Y.one('#arrow-right').setStyle('borderLeftColor','#bbbbbb');
            socket.emit('drive', { key:'right-arrow', status:'up'});
            
        }else if(e.keyCode == 40){
            Y.one('#arrow-down').setStyle('borderTopColor','#bbbbbb');
            socket.emit('drive', { key:'down-arrow', status:'up'});
            
        }
    });
    
    
    var arrows = {};
    var timerids = {};
    var hold = {};
    var stylemap = {'up':'borderBottomColor', 'down':'borderTopColor', 'left':'borderRightColor', 'right':'borderLeftColor'};
    var preparrow = function(d){
        arrows[d] = Y.one('#arrow-'+d);
        hold[d] = function(){
            socket.emit('drive', { key:d+'-arrow', status:'down'});
            timerids[d] = setTimeout(hold[d], 750);
        };
        arrows[d].on('mousedown', function(e){
            e.target.setStyle(stylemap[d],'#000000');
            hold[d]();
        });
        arrows[d].on('mouseup', function(e){
            e.target.setStyle(stylemap[d],'#bbbbbb');
            socket.emit('drive', { key:d+'-arrow', status:'up'});
            clearTimeout(timerids[d]);
        });
    };
    preparrow('up');
    preparrow('down');
    preparrow('left');
    preparrow('right');
    
    
    
    
    
    var vs = Y.one("#videostream");
    var vsc = Y.one("#videostreamcontainer");
    vsc.setStyle('width', vs.getStyle('width'));
    vsc.setStyle('height', vs.getStyle('height'));
    
    
});

