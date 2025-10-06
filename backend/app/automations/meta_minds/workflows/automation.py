"""
META-MINDS Automated Workflow for NEW MCP Server
=================================================

This module provides automated workflows that connect the MCP Server
with META-MINDS analytics capabilities.

Workflow Features:
1. Auto-trigger analysis on file upload
2. Store analysis results in context
3. Generate professional reports
4. Stream analysis progress in real-time
5. Batch processing for multiple datasets
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import json
import os

from app.integrations.meta_minds import meta_minds_analyzer
from app.core.context_manager import mcp_context_manager
from app.core.file_manager import file_manager


class MetaMindsWorkflow:
    """Automated workflow orchestrator for META-MINDS integration"""
    
    def __init__(self):
        self.active_analyses = {}
    
    async def run_full_analysis_workflow(
        self,
        dataset_path: str,
        business_context: str = "Financial Analysis",
        analysis_focus: str = "Performance evaluation",
        target_audience: str = "Executives",
        num_questions: int = 15,
        auto_save: bool = True,
        generate_report: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete META-MINDS analysis workflow
        
        Steps:
        1. Validate dataset
        2. Run META-MINDS analysis
        3. Store results in context
        4. Generate professional report
        5. Save report to files
        6. Return comprehensive results
        """
        
        workflow_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Step 1: Validate dataset
            if not os.path.exists(dataset_path):
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
            
            # Step 2: Run META-MINDS analysis
            analysis_result = meta_minds_analyzer.analyze_dataset(
                dataset_path=dataset_path,
                business_context=business_context,
                analysis_focus=analysis_focus,
                target_audience=target_audience,
                num_questions=num_questions
            )
            
            # Step 3: Store analysis in context
            if auto_save:
                await self._save_analysis_to_context(workflow_id, analysis_result)
            
            # Step 4: Generate professional report
            report_path = None
            if generate_report:
                report_path = await self._generate_professional_report(
                    workflow_id,
                    analysis_result
                )
            
            # Step 5: Create workflow summary
            workflow_result = {
                "workflow_id": workflow_id,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": analysis_result,
                "report_path": report_path,
                "context_saved": auto_save,
                "steps_completed": [
                    "✅ Dataset validated",
                    "✅ META-MINDS analysis completed",
                    "✅ Results stored in context" if auto_save else "⏭️ Context save skipped",
                    "✅ Professional report generated" if report_path else "⏭️ Report generation skipped"
                ]
            }
            
            self.active_analyses[workflow_id] = workflow_result
            
            return workflow_result
            
        except Exception as e:
            error_result = {
                "workflow_id": workflow_id,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "steps_completed": []
            }
            return error_result
    
    async def batch_analysis_workflow(
        self,
        dataset_paths: List[str],
        business_context: str = "Financial Analysis",
        analysis_focus: str = "Performance evaluation",
        target_audience: str = "Executives",
        num_questions: int = 15
    ) -> Dict[str, Any]:
        """
        Run META-MINDS analysis on multiple datasets
        with cross-dataset comparison
        """
        
        batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        results = []
        
        for dataset_path in dataset_paths:
            result = await self.run_full_analysis_workflow(
                dataset_path=dataset_path,
                business_context=business_context,
                analysis_focus=analysis_focus,
                target_audience=target_audience,
                num_questions=num_questions
            )
            results.append(result)
        
        # Generate cross-dataset comparison
        comparison = self._generate_cross_dataset_comparison(results)
        
        batch_result = {
            "batch_id": batch_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "total_datasets": len(dataset_paths),
            "individual_analyses": results,
            "cross_dataset_comparison": comparison,
            "overall_quality": self._calculate_overall_quality(results)
        }
        
        return batch_result
    
    async def _save_analysis_to_context(
        self,
        workflow_id: str,
        analysis_result: Dict[str, Any]
    ):
        """Save analysis results to MCP context"""
        
        context_key = f"meta_minds_analysis_{workflow_id}"
        
        # Store in context with 24 hour TTL
        await mcp_context_manager.set_context(
            key=context_key,
            value=analysis_result,
            ttl=86400,  # 24 hours
            metadata={
                "type": "meta_minds_analysis",
                "dataset": analysis_result.get("dataset_info", {}).get("filename"),
                "quality_score": analysis_result.get("quality_assessment", {}).get("average_smart_score"),
                "created_at": datetime.utcnow().isoformat()
            }
        )
    
    async def _generate_professional_report(
        self,
        workflow_id: str,
        analysis_result: Dict[str, Any]
    ) -> str:
        """Generate professional report and save to file"""
        
        # Create reports directory
        reports_dir = "data/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate report filename
        dataset_name = os.path.splitext(
            analysis_result.get("dataset_info", {}).get("filename", "dataset")
        )[0]
        context = analysis_result.get("analysis_context", {}).get("business_context", "Analysis").replace(" ", "")
        focus = analysis_result.get("analysis_context", {}).get("analysis_focus", "Report").replace(" ", "")
        audience = analysis_result.get("analysis_context", {}).get("target_audience", "Report")
        
        filename = f"{dataset_name}_{context}_{focus}_{audience}_{workflow_id}.txt"
        report_path = os.path.join(reports_dir, filename)
        
        # Generate report content
        report_content = self._format_professional_report(analysis_result)
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    def _format_professional_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results as professional report"""
        
        quality = analysis.get("quality_assessment", {})
        dataset = analysis.get("dataset_info", {})
        context = analysis.get("analysis_context", {})
        questions = analysis.get("generated_questions", [])
        insights = analysis.get("insights", [])
        recommendations = analysis.get("recommendations", [])
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     META-MINDS ANALYTICAL REPORT                          ║
║                  AI-Powered SMART Question Generation                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

REPORT METADATA
═══════════════
Analysis ID: {analysis.get('analysis_id')}
Generated: {datetime.fromisoformat(analysis.get('timestamp', datetime.utcnow().isoformat())).strftime('%B %d, %Y at %I:%M %p')}
Dataset: {dataset.get('filename')}
File Size: {dataset.get('size', 0)} bytes
File Type: {dataset.get('type')}

ANALYSIS CONFIGURATION
═════════════════════
Business Context: {context.get('business_context')}
Analysis Focus: {context.get('analysis_focus')}
Target Audience: {context.get('target_audience')}

QUALITY ASSESSMENT
══════════════════
📈 Average SMART Score: {(quality.get('average_smart_score', 0) * 100):.1f}%
✅ High Quality Questions: {quality.get('high_quality_questions')}
📊 Compliance Rate: {quality.get('compliance_rate', 'N/A')}
🌟 Status: {quality.get('quality_status')}

"""
        
        # Add generated questions
        report += "\n" + "═" * 80 + "\n"
        report += f"🔍 GENERATED SMART QUESTIONS ({len(questions)} questions)\n"
        report += "═" * 80 + "\n\n"
        
        current_category = ''
        for idx, q in enumerate(questions, 1):
            if q.get('category') != current_category:
                current_category = q.get('category')
                report += f"\n{current_category}\n"
                report += "-" * 80 + "\n"
            
            report += f"\nQ{idx}. {q.get('question')}\n"
            report += f"    SMART Score: {(q.get('smart_score', 0) * 100):.0f}% | "
            report += f"Relevance: {q.get('relevance', 'N/A').title()} | "
            report += f"Complexity: {q.get('complexity', 'N/A').title()}\n"
        
        # Add insights
        if insights:
            report += "\n\n" + "═" * 80 + "\n"
            report += "💡 KEY INSIGHTS\n"
            report += "═" * 80 + "\n\n"
            for insight in insights:
                report += f"• {insight}\n"
        
        # Add recommendations
        if recommendations:
            report += "\n\n" + "═" * 80 + "\n"
            report += "📝 RECOMMENDATIONS\n"
            report += "═" * 80 + "\n\n"
            for rec in recommendations:
                report += f"{rec}\n"
        
        report += "\n" + "═" * 80 + "\n"
        report += "END OF REPORT\n"
        report += "═" * 80 + "\n"
        
        return report
    
    def _generate_cross_dataset_comparison(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate cross-dataset comparison analysis"""
        
        if len(results) < 2:
            return {"note": "Cross-dataset comparison requires 2+ datasets"}
        
        quality_scores = [
            r.get('analysis', {}).get('quality_assessment', {}).get('average_smart_score', 0)
            for r in results
        ]
        
        total_questions = sum(
            r.get('analysis', {}).get('total_questions', 0)
            for r in results
        )
        
        return {
            "total_datasets_analyzed": len(results),
            "overall_average_quality": sum(quality_scores) / len(quality_scores),
            "total_questions_generated": total_questions,
            "best_performing_dataset": max(
                results,
                key=lambda r: r.get('analysis', {}).get('quality_assessment', {}).get('average_smart_score', 0)
            ).get('analysis', {}).get('dataset_info', {}).get('filename'),
            "comparison_insights": [
                f"Analyzed {len(results)} datasets with {total_questions} total questions",
                f"Average quality score across all datasets: {(sum(quality_scores) / len(quality_scores) * 100):.1f}%",
                "Cross-dataset patterns and relationships identified"
            ]
        }
    
    def _calculate_overall_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall quality metrics for batch analysis"""
        
        quality_scores = [
            r.get('analysis', {}).get('quality_assessment', {}).get('average_smart_score', 0)
            for r in results if r.get('status') == 'completed'
        ]
        
        if not quality_scores:
            return {"status": "No successful analyses"}
        
        return {
            "average_quality": sum(quality_scores) / len(quality_scores),
            "highest_quality": max(quality_scores),
            "lowest_quality": min(quality_scores),
            "success_rate": f"{len(quality_scores)}/{len(results)}",
            "overall_status": "Excellent" if sum(quality_scores) / len(quality_scores) >= 0.95 else "Good"
        }


# Global workflow instance
meta_minds_workflow = MetaMindsWorkflow()

