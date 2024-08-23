package com.example.bixolon_printer;

import androidx.annotation.NonNull;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.flutter.embedding.engine.plugins.FlutterPlugin;
import io.flutter.plugin.common.MethodCall;
import io.flutter.plugin.common.MethodChannel;
import io.flutter.plugin.common.MethodChannel.MethodCallHandler;
import io.flutter.plugin.common.MethodChannel.Result;

import com.bixolon.labelprinter.BixolonLabelPrinter;

/** BixolonPrinterPlugin */
public class BixolonPrinterPlugin implements FlutterPlugin, MethodCallHandler {
  /// The MethodChannel that will the communication between Flutter and native Android
  ///
  /// This local reference serves to register the plugin with the Flutter Engine and unregister it
  /// when the Flutter Engine is detached from the Activity
  private MethodChannel channel;
  private BixolonLabelPrinter bixolonLabelPrinter;
  private Handler handler;
  private Context context;

  private String TAG = "Bixolon Printer";

  @Override
  public void onAttachedToEngine(@NonNull FlutterPluginBinding flutterPluginBinding) {
    channel = new MethodChannel(flutterPluginBinding.getBinaryMessenger(), "bixolon_printer");
    channel.setMethodCallHandler(this);

	// backgroundThread.start();
    context = flutterPluginBinding.getApplicationContext();
	bixolonLabelPrinter = new BixolonLabelPrinter(context);
  }

  @Override
  public void onMethodCall(@NonNull MethodCall call, @NonNull Result result) {
    Log.d(TAG, "onMethodCall: " + call.method);

    switch (call.method) {
      case "findBluetoothPrinter":
        findBluetoothPrinter(result);
        break;
      case "connectPrinter":
        connectPrinter(call.argument("address"), result);
        break;
      case "printQr":
        printQr(call.argument("image"), call.argument("isTransparent"), call.argument("x"), call.argument("y"), call.argument("width"), call.argument("threshold"), call.argument("ditheringType"), call.argument("compressType"), call.argument("rotation"), result);
        break;
      default: 
        result.notImplemented();
        break;
    }
  }

	@Override
	public void onDetachedFromEngine(@NonNull FlutterPluginBinding binding) {
		channel.setMethodCallHandler(null);
	}
	
	// 휴대폰에 연결된 블루투스 장치 리스트를 반환하는 함수
  private void findBluetoothPrinter(@NonNull Result result) {
    try {
      BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
      Set<BluetoothDevice> bondedDeviceSet = bluetoothAdapter.getBondedDevices();

      List<String> bondedDevices = new ArrayList<>();
      for (BluetoothDevice device : bondedDeviceSet) {
        bondedDevices.add(device.getName() + "("+ device.getAddress() + ")");
        Log.d(TAG, device.getName());
      }

      result.success(bondedDevices);
    } catch (Exception e) {
      result.error("BLUETOOTH_ERROR", "No bluetooth permission", null);
    }
  }

  // 프린터기에 연결하는 함수
  private boolean connectPrinter(String address, @NonNull Result result) {
    if (bixolonLabelPrinter == null) {
      bixolonLabelPrinter = new BixolonLabelPrinter(context);
    }

    if (address == null) {
      result.error("CONNECTION_ERROR", "Invalid device address", false);
      return false;
    }

    bixolonLabelPrinter.connect(address);
    boolean isConnected = bixolonLabelPrinter.isConnected();

    result.success(isConnected);
    return isConnected;
  }

  // 전송 받은 QR 코드를 프린트하는 함수
  private void printQr(String image, boolean isTransparent, int x, int y, int width, int threshold, int ditheringType, int compressType, int rotation, @NonNull Result result) {
    if (!bixolonLabelPrinter.isConnected()) {
      result.error("CONNECTION_ERROR", "Bluetooth printer not connected", false);
    }
    
    bixolonLabelPrinter.drawBase64Image(image, isTransparent, x, y, width, threshold, ditheringType, compressType, rotation);
    bixolonLabelPrinter.print(1, 1);
  
    result.success(true);
  }
}

