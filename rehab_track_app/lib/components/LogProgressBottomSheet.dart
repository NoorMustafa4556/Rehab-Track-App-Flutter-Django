import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../view_models/ClinicianViewModel.dart';

class LogProgressBottomSheet extends StatefulWidget {
  final int patientId;
  final String patientName;

  const LogProgressBottomSheet({super.key, required this.patientId, required this.patientName});

  static void show(BuildContext context, int patientId, String patientName) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
          child: LogProgressBottomSheet(patientId: patientId, patientName: patientName),
        );
      },
    );
  }

  @override
  State<LogProgressBottomSheet> createState() => _LogProgressBottomSheetState();
}

class _LogProgressBottomSheetState extends State<LogProgressBottomSheet> {
  final _formKey = GlobalKey<FormState>();
  String _treatmentGiven = '';
  String _notes = '';
  Map<String, dynamic> _metricsData = {};
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await Provider.of<ClinicianViewModel>(context, listen: false).fetchPatientDetail(widget.patientId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final clinicianVM = Provider.of<ClinicianViewModel>(context);

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: clinicianVM.isLoading && _isSubmitting == false
            ? const Center(child: CircularProgressIndicator(color: AppColors.darkTeal))
            : Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Log Progress: ${widget.patientName}',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.darkTeal),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: AppColors.secondaryText),
                          onPressed: () => Navigator.pop(context),
                        )
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 12),
                    TextFormField(
                      decoration: InputDecoration(
                        labelText: 'Treatment Given',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                      onSaved: (val) => _treatmentGiven = val ?? '',
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      decoration: InputDecoration(
                        labelText: 'Clinician Notes',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      maxLines: 3,
                      onSaved: (val) => _notes = val ?? '',
                    ),
                    const SizedBox(height: 24),
                    const Text('Metrics:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.darkTeal)),
                    const SizedBox(height: 12),
                    if (clinicianVM.availableMetrics.isEmpty)
                      const Text('No metrics available.', style: TextStyle(color: Colors.grey))
                    else
                      ...clinicianVM.availableMetrics.map((metric) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: TextFormField(
                            decoration: InputDecoration(
                              labelText: '${metric['metric_name']} (${metric['unit']})',
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                              hintText: 'Min: ${metric['min_value']}, Max: ${metric['max_value']}',
                            ),
                            keyboardType: TextInputType.number,
                            onSaved: (val) {
                              if (val != null && val.isNotEmpty) {
                                _metricsData[metric['id'].toString()] = val;
                              }
                            },
                          ),
                        );
                      }),
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.darkTeal,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        onPressed: _isSubmitting
                            ? null
                            : () async {
                                if (_formKey.currentState!.validate()) {
                                  _formKey.currentState!.save();
                                  setState(() => _isSubmitting = true);
                                  
                                  bool success = await clinicianVM.addProgressLog(
                                    widget.patientId,
                                    _treatmentGiven,
                                    _notes,
                                    _metricsData,
                                  );
                                  
                                  setState(() => _isSubmitting = false);
                                  
                                  if (success && context.mounted) {
                                    Navigator.pop(context);
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('Progress Logged Successfully!')),
                                    );
                                  }
                                }
                              },
                        child: _isSubmitting
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text('Submit Progress', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }
}
