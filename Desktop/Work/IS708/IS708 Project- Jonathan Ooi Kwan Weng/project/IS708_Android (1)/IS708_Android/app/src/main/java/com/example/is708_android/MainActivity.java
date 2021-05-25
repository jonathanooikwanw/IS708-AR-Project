package com.example.is708_android;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.util.Log;
import android.view.MotionEvent;
import android.view.PixelCopy;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Locale;
import com.androidnetworking.*;
import com.google.ar.core.Anchor;
import com.google.ar.core.HitResult;
import com.google.ar.core.Plane;
import com.google.ar.core.Pose;
import com.google.ar.core.Session;
import com.google.ar.sceneform.AnchorNode;
import com.google.ar.sceneform.ArSceneView;
import com.google.ar.sceneform.Scene;
import com.google.ar.sceneform.math.Vector3;

import com.google.ar.sceneform.rendering.MaterialFactory;
import com.google.ar.sceneform.rendering.ModelRenderable;
import com.google.ar.sceneform.rendering.ShapeFactory;
import com.google.ar.sceneform.ux.ArFragment;
import com.google.ar.sceneform.ux.TransformableNode;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import com.google.gson.internal.$Gson$Types;

public class MainActivity extends AppCompatActivity {
    private static final String[] PERMISSIONS = {
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.INTERNET,
            Manifest.permission.CAMERA,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
    };

    public static final Integer MULTIPLE_PERMISSIONS = 10;
    private SpeechRecognizer speechRecognizer;
    private EditText editText;
    private ImageView upArrow;
    private ImageView downArrow;
    private ImageButton micButton;
    private int gestureChoice;
    // To help you see what's going on from the UI itself
    private TextView sysMsgTextView;

    // AR
    private ModelRenderable gestureResponseRenderable;
    private ArFragment fragment;
    private TransformableNode responseObjectNode;
    private String targetScreenArea = null;

    //Objects drawn on the screen depending on gesture received
    private ImageView cubeLeft;
    private ImageView cubeRight;
    private ImageView sphereLeft;
    private ImageView sphereRight;
    private ImageView boundingBoxDraw;
    private Canvas canvas;

    //To get the bitmap height and width and mid point
    private Bitmap bitmap2 = null;
    float height;
    float width;
    float bitmapMidpoint;
    float midX, midY;


    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        for(String p:PERMISSIONS) {
            if(ContextCompat.checkSelfPermission(this,p) != PackageManager.PERMISSION_GRANTED){
                checkPermission();
            }
        }

        sysMsgTextView = findViewById(R.id.sysMessageTextView);
        sysMsgTextView.setText("");

        // Is SpeechRecognizer available?
        if (SpeechRecognizer.isRecognitionAvailable(this)){
            Log.d(String.valueOf(this),"Recognition is available");
            sysMsgTextView.setText("Speech recognition is available");
        } else {
            Log.d(String.valueOf(this),"Recognition is *NOT* available");
            sysMsgTextView.setText("Speech recognition is *NOT* available");
        }
        // Initialize AndroidNetworking
        AndroidNetworking.initialize(getApplicationContext());

        editText = findViewById(R.id.text);
        upArrow = findViewById(R.id.upArrowImage);
        downArrow = findViewById(R.id.downArrowImage);
        micButton = findViewById(R.id.micButton);
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);

        //The cubes/spheres which will be rendered depending on gesture
        cubeLeft = findViewById(R.id.cubeLeft);
        cubeRight = findViewById(R.id.cubeRight);
        sphereLeft = findViewById(R.id.sphereLeft);
        sphereRight = findViewById(R.id.sphereRight);

        //The canvas where the bounding box will be drawn
        boundingBoxDraw = findViewById(R.id.boundingBoxDraw);

        //Hides the objects on startup
        cubeLeft.setVisibility(View.GONE);
        cubeRight.setVisibility(View.GONE);
        sphereLeft.setVisibility(View.GONE);
        sphereRight.setVisibility(View.GONE);

        final Intent speechRecognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
        speechRecognizer.setRecognitionListener(new RecognitionListener() {
            @Override
            public void onReadyForSpeech(Bundle bundle) {
            }

            @Override
            public void onBeginningOfSpeech() {
                editText.setHint("...Listening...");
            }

            @Override
            public void onRmsChanged(float v) {
            }

            @Override
            public void onBufferReceived(byte[] bytes) {
            }

            @Override
            public void onEndOfSpeech() {
            }

            @Override
            public void onError(int i) {
            }

            //Not sure why is this needed
            @RequiresApi(api = Build.VERSION_CODES.N)
            @Override
            public void onResults(Bundle bundle) {
                ArrayList<String> data = bundle.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                String commandText = null;
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    commandText = String.join(" ",data);
                }
                editText.setText(commandText);
                Log.d(String.valueOf(this), "Result: " + commandText);
                sysMsgTextView.setText(sysMsgTextView.getText() + "\n" + "Speech recognition done");
                takePhoto();


                //Handler is added to introduce a delay - else a connection error will occur.
                String finalCommandText = commandText;
                new Handler().postDelayed(new Runnable() {
                    @Override
                    public void run(){
                        CommModule.callTargetDetectionApi(finalCommandText, MainActivity.this);
                    }
                }, 5000);
            }

            @Override
            public void onPartialResults(Bundle bundle) {

            }

            @Override
            public void onEvent(int i, Bundle bundle) {

            }
        });

        micButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {
                if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    speechRecognizer.stopListening();
                    Log.d(String.valueOf(this), "Stopped listening");
                }
                if (motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    speechRecognizer.startListening(speechRecognizerIntent);
                    Log.d(String.valueOf(this),"Started listening");
                    return true;
                }
                return false;
            }
        });

        // AR
        fragment = (ArFragment) getSupportFragmentManager().findFragmentById(R.id.sceneform_fragment);
        // Hide instruction animation
        fragment.getPlaneDiscoveryController().hide();
        fragment.getPlaneDiscoveryController().setInstructionView(null);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        speechRecognizer.destroy();
    }

    private void checkPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            ActivityCompat.requestPermissions(this,PERMISSIONS,MULTIPLE_PERMISSIONS);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == MULTIPLE_PERMISSIONS && grantResults.length > 0 ){
            if(grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Permission Granted", Toast.LENGTH_SHORT).show();
            }
        }
    }

    public void clickUpArrow(View view) {
        gestureChoice=1;
        CommModule.callGestureDetectionApi(gestureChoice, MainActivity.this);
    }

    public void clickDownArrow(View view) {
        gestureChoice=2;
        CommModule.callGestureDetectionApi(gestureChoice,MainActivity.this);
    }

    public void selectTargetScreenArea(String boundingBoxJson) {

        //Get the height and width of the image taken by the camera
        height = bitmap2.getHeight();
        width = bitmap2.getWidth();

        //Calculate the x midpoint of the image - used to determine if bounding box is left or right on the image
        bitmapMidpoint = width/2;

        //(‘bottle’,[0,0,100,100]) will become bottle 0 0 100 100 split into 5 different strings
        String delims = "[,'\\[\\]]+";
        String[] tokens = boundingBoxJson.split(delims);
        float xLeft = Float.parseFloat(tokens[3]);
        float yTop = Float.parseFloat(tokens[4]);
        float xRight = Float.parseFloat(tokens[5]);
        float yBottom = Float.parseFloat(tokens[6]);

        //Calculate the midpoint of the bounding box
        midX = (xLeft + xRight) / 2;

        /*if the midpoint of the bounding box is larger than the midpoint of the entire bitmap/image, we can safely assume that the
          bounding box is mostly on the right side, and vice versa for the left side (if smaller than midpoint)
         */
        if (midX < bitmapMidpoint) {
            targetScreenArea = "LEFT";
        }
        else if (midX > bitmapMidpoint)
        {
            targetScreenArea = "RIGHT";
        }

        /*   Bounding box rendering    */
        //Preparing the canvas for drawing bounding box
        int w = (int)width;
        int h = (int)height;

        //Bitmap setup and assignment to canvas
        Bitmap.Config conf = Bitmap.Config.ARGB_8888;
        Bitmap bmp = Bitmap.createBitmap(w, h, conf); // this creates a MUTABLE bitmap
        canvas = new Canvas(bmp);

        // Draws the bounding box using the coordinates from the server API
        Paint myPaint = new Paint();
        myPaint.setStyle(Paint.Style.STROKE);
        myPaint.setColor(Color.rgb(0, 0, 255));
        myPaint.setStrokeWidth(10);
        canvas.drawRect(xLeft, yTop, xRight, yBottom, myPaint);
        boundingBoxDraw.setImageBitmap(bmp);


    }


    public void respondToGesture(String gesture) {
        String nodding = "\"Nodding\"";
        String shaking = "\"Shaking\"";

        //If bounding box is on the left side of the screen, we render the object on the left
        if (targetScreenArea.equals("LEFT"))
        {

            //If the gesture is nodding(gesture 1), we draw a cube and hide the sphere if it exists
            if (gesture.equals(nodding))
            {
                cubeLeft.setVisibility(View.VISIBLE);
                sphereLeft.setVisibility(View.GONE);
                cubeRight.setVisibility(View.GONE);
                sphereRight.setVisibility(View.GONE);
            }

            //If the gesture is nodding(gesture 1), we draw a sphere and hide the cube if it exists
            else if (gesture.equals(shaking))
            {
                sphereLeft.setVisibility(View.VISIBLE);
                sphereRight.setVisibility(View.GONE);
                cubeRight.setVisibility(View.GONE);
                cubeLeft.setVisibility(View.GONE);
            }
        }

        //If bounding box is on the right side of the screen, we render the object on the right
        else if (targetScreenArea.equals("RIGHT")){

            //If the gesture is nodding(gesture 1), we draw a cube and hide the sphere if it exists
            if (gesture.equals(nodding))
            {
                cubeRight.setVisibility(View.VISIBLE);
                cubeLeft.setVisibility(View.GONE);
                sphereLeft.setVisibility(View.GONE);
                sphereRight.setVisibility(View.GONE);
            }

            //If the gesture is nodding(gesture 1), we draw a sphere and hide the cube if it exists
            else if (gesture.equals(shaking))
            {
                sphereRight.setVisibility(View.VISIBLE);
                sphereLeft.setVisibility(View.GONE);
                cubeLeft.setVisibility(View.GONE);
                cubeRight.setVisibility(View.GONE);
            }
        }
    }

    public void resetAppUi(View view){
        if(null != responseObjectNode) {
            responseObjectNode.setParent(null);
            responseObjectNode = null;
        }

        editText.setText(R.string.tap_button_to_speak);
        sysMsgTextView.setText("");
        targetScreenArea = null;

        //hides the objects when ui is reset
        cubeLeft.setVisibility(View.GONE);
        cubeRight.setVisibility(View.GONE);
        sphereLeft.setVisibility(View.GONE);
        sphereRight.setVisibility(View.GONE);

        canvas.drawColor(0, PorterDuff.Mode.CLEAR);

    }

    // Camera
    // Not sure why this needed
    @RequiresApi(api = Build.VERSION_CODES.N)
    private void takePhoto() {
        String targetFileFullPath = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES) + "/is708.jpg";
        ArSceneView arSceneView = fragment.getArSceneView();

        // Create a bitmap the size of the scene view.
        //Returns a mutable bitmap with the specified width and height. - currently nothing inside
        final Bitmap bitmap = Bitmap.createBitmap(arSceneView.getWidth(), arSceneView.getHeight(), Bitmap.Config.ARGB_8888);

        // Create a handler thread to offload the processing of the image.
        final HandlerThread handlerThread = new HandlerThread("PixelCopier");
        handlerThread.start();
        // Make the request to copy.
        PixelCopy.request(arSceneView, bitmap, (copyResult) -> {
            if (copyResult == PixelCopy.SUCCESS) {
                try {
                    saveImageBitmapToDisk(bitmap, targetFileFullPath);
                } catch (IOException e) {
                    Toast toast = Toast.makeText(MainActivity.this, e.toString(), Toast.LENGTH_LONG);
                    toast.show();
                    return;
                }
                Log.d("takePhoto()", "Screenshot saved in " + targetFileFullPath);
                bitmap2 = bitmap;
                sysMsgTextView.setText(sysMsgTextView.getText() + "\n" + "Screenshot saved to"  + targetFileFullPath);
            } else {
                Log.e("takePhoto()","Failed to take screenshot");
                sysMsgTextView.setText(sysMsgTextView.getText() + "Failed to take screenshot");
            }
            handlerThread.quitSafely();
        }, new Handler(handlerThread.getLooper()));
    }


    public void saveImageBitmapToDisk(Bitmap bitmap, String targetFileFullPath) throws IOException {
        File sceneImageFile = new File(targetFileFullPath);
        FileOutputStream fileOutputStream = new FileOutputStream(sceneImageFile);
        bitmap.compress(Bitmap.CompressFormat.JPEG, 70, fileOutputStream);
        fileOutputStream.flush();
        fileOutputStream.close();
    }

    public void displayMessage(String s) {
        sysMsgTextView.setText(s);
    }
}
