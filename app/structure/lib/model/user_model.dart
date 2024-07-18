//
//
// 유저 모델.
//
//

import 'dart:convert';

import 'package:flutter/material.dart';

class UserModel with ChangeNotifier {
  String? userId;
  String? name;
  String? homeAdress;
  String? company;
  String? jobTitle;
  String? type;
  bool? alarm;
  String? createdAt;
  bool auto = false; // 자동 로그인 여부

  // 회원가입시 임시 password 저장
  String? password;

  // Constructor
  UserModel({
    this.userId,
    this.name,
    this.homeAdress,
    this.company,
    this.jobTitle,
    this.type,
    this.createdAt,
    this.alarm,
    this.password,
  });

  /// 유저 정보 모델에 저장
  void fromJson(Map<String, dynamic> jsonData) {
    userId = jsonData['userId'];
    name = jsonData['name'];
    homeAdress = jsonData['homeAddr'];
    company = jsonData['company'];
    jobTitle = jsonData['jobTitle'];
    type = jsonData['type'];
    alarm = jsonData['alarm'];
    createdAt = jsonData['createdAt'];
  }

  /// 유저 정보 초기화
  void reset() {
    userId = null;
    name = null;
    homeAdress = null;
    company = null;
    jobTitle = null;
    type = null;
    alarm = null;
    createdAt = null;
    auto = false;
  }

  String toJson() {
    Map<String, dynamic> data = {
      "userId": userId,
      "name": name,
      "homeAddr": homeAdress,
      "company": company,
      "jobTitle": jobTitle,
      "type": type,
      "alarm": alarm,
    };

    return jsonEncode(data);
  }

  // @override
  // String toString() {
  //   return 'userId:$userId,'
  //       'name:$name,'
  //       'homeAdress:$homeAdress,'
  //       'company:$company,'
  //       'jobTitle:$jobTitle,'
  //       'type:$type,'
  //       'alarm:$alarm,'
  //       'createdAt:$createdAt,';
  // }
}
