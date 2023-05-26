var btnStart = document.getElementById( "btn-start" );
var btnStop = document.getElementById( "btn-stop" );
var btnCapture = document.getElementById( "btn-capture" );

var loadingOverlay = document.getElementById('loading-overlay');

// The stream & capture
var stream = document.getElementById( "stream" );
var capture = document.getElementById( "capture" );
var snapshot = document.getElementById( "snapshot" );

// The video stream
var cameraStream = null;

// Attach listeners
btnStart.addEventListener( "click", startStreaming );
btnStop.addEventListener( "click", stopStreaming );
btnCapture.addEventListener( "click", captureSnapshot );

// Start Streaming
function startStreaming() {

  var mediaSupport = 'mediaDevices' in navigator;

  if( mediaSupport && null == cameraStream ) {
    var divicon = document.getElementById("face-icon");
    divicon.style.display = 'none';
    btnStart.style.display = 'none';
    btnCapture.style.display = 'block';
    btnStop.style.display = 'block';

    navigator.mediaDevices.getUserMedia( { video: true } )
    .then( function( mediaStream ) {

      cameraStream = mediaStream;

      stream.srcObject = mediaStream;

      stream.play();
    })
    .catch( function( err ) {

      console.log( "Unable to access camera: " + err );
    });
  }
  else {

    alert( 'Your browser does not support media devices.' );

    return;
  }
}

// Stop Streaming
function stopStreaming() {

  if( null != cameraStream ) {
    var divicon = document.getElementById("face-icon");
    divicon.style.display = 'block';
    btnStart.style.display = 'block';
    btnCapture.style.display = 'none';
    btnStop.style.display = 'none';

    var track = cameraStream.getTracks()[ 0 ];

    track.stop();
    stream.load();

    cameraStream = null;
  }
}

function captureSnapshot() {

  if( null != cameraStream ) {

    btnStart.style.display = 'none';
    btnCapture.style.display = 'none';
    btnStop.style.display = 'none';

    loadingOverlay.style.display = 'block';

    var ctx = capture.getContext( '2d' );
    var img = new Image();

    ctx.drawImage( stream, 0, 0, capture.width, capture.height );
  
    img.src   = capture.toDataURL( "image/png" );
    img.width = 240;

    snapshot.innerHTML = '';

    snapshot.appendChild( img );

    //var img_blob = dataURItoBlob( img.src )
    //console.log(img);
    //console.log(img.src);

    var request = new XMLHttpRequest();

    request.open( "POST", "/login", true );
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var jsonResponse = JSON.parse(this.responseText);
            console.log(jsonResponse);
            if(jsonResponse.is_picture_known == false){ 
                btnStart.style.display = 'block';
                loadingOverlay.style.display = 'none';
              swal("Invalid Login", "Your face is not recognized!", "error");
            }else{
              window.location.replace("http://127.0.0.1:5000/");
            }

        }
    };

    var data	= new FormData();
    var dataURI	= snapshot.firstChild.getAttribute( "src" );
    var imageData   = dataURItoBlob( img.src );

    var inputElement = document.getElementById('natid');

    // Get the value of the input
    var natid = inputElement.value;

    data.append( "file", imageData, "file.png" );
    data.append("natid", natid);
    console.log(imageData);
    request.send( data );
    }
}

function dataURItoBlob( dataURI ) {

	var byteString = atob( dataURI.split( ',' )[ 1 ] );
	var mimeString = dataURI.split( ',' )[ 0 ].split( ':' )[ 1 ].split( ';' )[ 0 ];
	
	var buffer	= new ArrayBuffer( byteString.length );
	var data	= new DataView( buffer );
	
	for( var i = 0; i < byteString.length; i++ ) {
	
		data.setUint8( i, byteString.charCodeAt( i ) );
	}
	
	return new Blob( [ buffer ], { type: mimeString } );
}