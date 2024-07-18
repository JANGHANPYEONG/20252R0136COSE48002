//
//
// local_data_source.
//
//

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

class LocalDataSource {
  /// 임시저장 데이터 POST
  static Future<dynamic> saveDataToLocal(String jsonData, String dest) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$dest.json');

      if (!await directory.exists()) {
        await directory.create(recursive: true);
      }

      dynamic response = await file.writeAsString(jsonData);
      debugPrint('임시저장 성공');
      return response;
    } catch (e) {
      debugPrint('임시저장 실패: $e');
      return;
    }
  }

  /// 임시저장 데이터 GET
  static Future<dynamic> getLocalData(String dest) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$dest.json');
      if (await file.exists()) {
        final response = await file.readAsString();
        debugPrint('임시저장 데이터 fetch 성공');
        return jsonDecode(response);
      } else {
        debugPrint('임시저장 데이터 없음');
        return;
      }
    } catch (e) {
      debugPrint('임시저장 데이터 읽기 실패: $e');
      return;
    }
  }

  /// 임시저장 데이터 삭제
  static Future<void> deleteLocalData(String dest) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/$dest.json');

      if (await file.exists()) {
        await file.delete();
        debugPrint('임시저장 데이터 삭제 성공');
      } else {
        debugPrint('삭제할 임시저장 데이터가 없음');
      }
    } catch (e) {
      debugPrint('임시저장 데이터 삭제 실패: $e');
    }
  }
}
