//
//
// 데이터 관리 tabbar 페이지(View) : Researcher
//
//

import 'package:flutter/material.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/screen/data_management/researcher/approve_data_screen.dart';
import 'package:structure/screen/data_management/researcher/data_management_home_researcher_screen.dart';

class DataManagementHomeTabScreen extends StatefulWidget {
  const DataManagementHomeTabScreen({super.key});

  @override
  State<DataManagementHomeTabScreen> createState() =>
      _DataManagementHomeTabScreenState();
}

class _DataManagementHomeTabScreenState
    extends State<DataManagementHomeTabScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: '데이터 관리',
        backButton: true,
        tabController: _tabController,
        tabs: const [
          Tab(text: '추가 정보 입력'),
          Tab(text: '일반데이터 승인'),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          DataManagementHomeResearcherScreen(),
          ApproveDataScreen(),
        ],
      ),
    );
  }
}
