import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  Uint8List? _imageBytes;
  String? _outputImageUrl;
  String? _diseaseName;
  String? _cause;
  String? _treatment;
  String? _prevention;
  bool _isLoading = false;

  final String apiUrl = "https://papaya-disease-detection.onrender.com/predict"; // Updated backend URL


  Future<void> pickImage() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: false,
    );

    if (result != null) {
      Uint8List fileBytes = result.files.first.bytes!;
      setState(() {
        _imageBytes = fileBytes;
        _isLoading = true;
        _diseaseName = null;
        _outputImageUrl = null;
        _cause = null;
        _treatment = null;
        _prevention = null;
      });
      await uploadImage(fileBytes);
    }
  }

  Future<void> uploadImage(Uint8List fileBytes) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse(apiUrl))
        ..files.add(http.MultipartFile.fromBytes('image', fileBytes, filename: "upload.jpg"));

      var response = await request.send();
      if (response.statusCode == 200) {
        var jsonResponse = jsonDecode(await response.stream.bytesToString());
        setState(() {
          // 🔹 **Force Image Refresh by Adding a Timestamp**
          _outputImageUrl = jsonResponse['image_url'] + "?timestamp=${DateTime.now().millisecondsSinceEpoch}";
          _diseaseName = jsonResponse['message'];
          _cause = jsonResponse['disease_info']['cause'];
          _treatment = jsonResponse['disease_info']['treatment'];
          _prevention = jsonResponse['disease_info']['prevention'];
        });
      } else {
        setState(() {
          _diseaseName = "Error in detection!";
        });
      }
    } catch (e) {
      setState(() {
        _diseaseName = "Failed to connect to server!";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Papaya Disease Detection')),
        body: SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            children: [
              ElevatedButton(onPressed: pickImage, child: Text("Select Image")),
              if (_diseaseName != null) 
                Text("Detected Disease: $_diseaseName", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.red)),
              if (_outputImageUrl != null)
                Image.network(_outputImageUrl!, height: 300, key: ValueKey(_outputImageUrl)), // 🔹 Ensure UI reloads the image
              if (_cause != null) Text("Cause: $_cause"),
              if (_treatment != null) Text("Treatment: $_treatment"),
              if (_prevention != null) Text("Prevention: $_prevention"),
            ],
          ),
        ),
      ),
    );
  }
}
