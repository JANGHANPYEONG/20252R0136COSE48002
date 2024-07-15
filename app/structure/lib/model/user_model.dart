//
//
// 유저 모델.
//
//

import 'package:flutter/material.dart';

class UserModel with ChangeNotifier {
  String? userId;
  String? password;
  String? name;
  String? homeAdress;
  String? company;
  String? jobTitle;
  String? type;
  String? createdAt;
  bool? alarm;
  bool auto = false;

  // Constructor
  UserModel({
    this.userId,
    this.password,
    this.name,
    this.homeAdress,
    this.company,
    this.jobTitle,
    this.type,
    this.createdAt,
    this.alarm,
  });

  // Data fetch
  void fromJson(Map<String, dynamic> jsonData) {
    userId = jsonData['userId'];
    name = jsonData['name'];
    password = jsonData['password']; // TODO : 삭제
    homeAdress = jsonData['homeAddr'];
    company = jsonData['company'];
    jobTitle = jsonData['jobTitle'];
    type = jsonData['type'];
    alarm = jsonData['alarm'];
    createdAt = jsonData['createdAt'];
  }

  // Data reset
  void reset() {
    userId = null;
    password = null;
    name = null;
    homeAdress = null;
    company = null;
    jobTitle = null;
    type = null;
    createdAt = null;
    alarm = null;
    auto = false;
  }

  @override
  String toString() {
    return 'userId:$userId,'
        'password:$password,'
        'name:$name,'
        'homeAdress:$homeAdress,'
        'company:$company,'
        'jobTitle:$jobTitle,'
        'type:$type,'
        'createdAt:$createdAt,'
        'alarm:$alarm,';
  }
}
