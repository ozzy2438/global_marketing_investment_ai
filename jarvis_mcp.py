#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS AI Agency OS — Claude Code / MCP Integration
=====================================================
JARVIS'in "mühendis" katmanı. Teknik işleri Claude Code'a delege eder.

MCP (Model Context Protocol) üzerinden:
- Website oluşturma
- Chatbot geliştirme
- Otomasyon kurulumu
- Kod üretimi
- Deployment

Kullanım:
    from jarvis_mcp import ClaudeCodeBridge
    bridge = ClaudeCodeBridge()
    result = bridge.delegate_task(task)
"""

import json
import os
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


# ============================================
# TASK TYPES
# ============================================
class TaskType(str, Enum):
    WEBSITE = "website"
    CHATBOT = "chatbot"
    AUTOMATION = "automation"
    LANDING_PAGE = "landing_page"
    BOOKING_SYSTEM = "booking_system"
    CRM_WIDGET = "crm_widget"
    REVIEW_SYSTEM = "review_system"
    SEO_OPTIMIZATION = "seo_optimization"
    SOCIAL_MEDIA_BOT = "social_media_bot"
    EMAIL_AUTOMATION = "email_automation"
    ANALYTICS_DASHBOARD = "analytics_dashboard"
    PAYMENT_INTEGRATION = "payment_integration"
    CUSTOM = "custom"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================
# MCP SERVER CONFIGURATION
# ============================================
class MCPConfig:
    """MCP Server yapılandırması"""

    DEFAULT_CONFIG = {
        "mcpServers": {
            "jarvis-agency": {
                "command": "node",
                "args": ["jarvis-mcp-server/index.js"],
                "env": {
                    "JARVIS_API_URL": "http://localhost:8000",
                    "JARVIS_DB_PATH": "./jarvis.db"
                }
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "./projects"]
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                }
            },
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            },
            "sqlite": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sqlite", "./jarvis.db"]
            }
        }
    }

    @staticmethod
    def generate_config(custom_servers: Dict = None) -> Dict:
        config = MCPConfig.DEFAULT_CONFIG.copy()
        if custom_servers:
            config["mcpServers"].update(custom_servers)
        return config

    @staticmethod
    def save_config(path: str = "mcp_config.json"):
        config = MCPConfig.generate_config()
        with open(path, "w") as f:
            json.dump(config, f, indent=2)
        return config


# ============================================
# SECTOR TEMPLATES — Claude Code'a gönderilecek
# ============================================
class SectorTemplates:
    """Sektör bazlı teknik şablonlar"""

    TEMPLATES = {
        "dental": {
            "website": {
                "pages": ["Ana Sayfa", "Hizmetler", "Doktorlar", "Galeri", "İletişim", "Online Randevu"],
                "features": [
                    "Online randevu formu + takvim entegrasyonu",
                    "Tedavi fiyat hesaplayıcı",
                    "Önce/Sonra galeri",
                    "WhatsApp canlı destek widget",
                    "Google Reviews entegrasyonu",
                    "Blog / Ağız sağlığı ipuçları",
                    "Doktor profil sayfaları",
                    "Responsive + mobil uyumlu"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "Supabase", "Cal.com API"],
                "estimated_hours": 40
            },
            "chatbot": {
                "intents": [
                    "randevu_al", "fiyat_sor", "tedavi_bilgi", "doktor_sec",
                    "konum_sor", "calisma_saatleri", "sigorta_sor", "acil_durum"
                ],
                "responses_count": 50,
                "channels": ["website_widget", "whatsapp", "instagram_dm"],
                "tech_stack": ["Dialogflow / Rasa", "WhatsApp Business API", "Node.js"],
                "estimated_hours": 30
            },
            "automation": {
                "workflows": [
                    {"name": "Randevu Hatırlatma", "trigger": "24h before appointment", "action": "WhatsApp + SMS"},
                    {"name": "Tedavi Takip", "trigger": "3 days after treatment", "action": "Satisfaction survey"},
                    {"name": "Review İsteme", "trigger": "7 days after treatment", "action": "Google Review link"},
                    {"name": "Kontrol Hatırlatma", "trigger": "6 months after last visit", "action": "WhatsApp + Email"},
                    {"name": "Doğum Günü", "trigger": "Patient birthday", "action": "Discount coupon"},
                    {"name": "Yeni Hasta Onboarding", "trigger": "New patient registered", "action": "Welcome sequence"}
                ],
                "tech_stack": ["n8n / Make.com", "WhatsApp Business API", "Google Calendar API"],
                "estimated_hours": 25
            }
        },
        "law_firm": {
            "website": {
                "pages": ["Ana Sayfa", "Uzmanlık Alanları", "Avukatlar", "Blog", "İletişim", "Online Danışma"],
                "features": [
                    "Online danışma randevu sistemi",
                    "Uzmanlık alanı filtreleme",
                    "Dava takip portalı (müvekkil girişi)",
                    "Blog + hukuki makaleler",
                    "Gizlilik odaklı tasarım",
                    "Avukat profil sayfaları",
                    "SSS bölümü",
                    "Responsive tasarım"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "Supabase", "Stripe"],
                "estimated_hours": 45
            },
            "chatbot": {
                "intents": [
                    "danisma_al", "uzmanlik_sor", "ucret_bilgi", "dava_takip",
                    "belge_gonder", "randevu_al", "acil_hukuki_destek", "referans"
                ],
                "responses_count": 60,
                "channels": ["website_widget", "whatsapp"],
                "tech_stack": ["Rasa", "WhatsApp Business API", "Python"],
                "estimated_hours": 35
            },
            "automation": {
                "workflows": [
                    {"name": "Müvekkil Intake", "trigger": "New inquiry", "action": "Auto-qualify + assign"},
                    {"name": "Dava Güncelleme", "trigger": "Case status change", "action": "Client notification"},
                    {"name": "Belge Hatırlatma", "trigger": "Missing documents", "action": "Email + WhatsApp"},
                    {"name": "Fatura Takip", "trigger": "Invoice overdue", "action": "Reminder sequence"},
                    {"name": "Duruşma Hatırlatma", "trigger": "3 days before hearing", "action": "SMS + Email"}
                ],
                "tech_stack": ["n8n", "Google Workspace API", "Twilio"],
                "estimated_hours": 30
            }
        },
        "gym": {
            "website": {
                "pages": ["Ana Sayfa", "Programlar", "Eğitmenler", "Fiyatlar", "Galeri", "Üye Ol"],
                "features": [
                    "Online üyelik satışı + ödeme",
                    "Ders programı takvimi",
                    "Eğitmen profilleri",
                    "Üye portalı (kişisel program)",
                    "Dönüşüm hikayeleri",
                    "BMI hesaplayıcı",
                    "Canlı doluluk göstergesi",
                    "Mobil uyumlu"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "Supabase", "Stripe/iyzico"],
                "estimated_hours": 35
            },
            "chatbot": {
                "intents": [
                    "uyelik_bilgi", "fiyat_sor", "ders_programi", "egitmen_sec",
                    "deneme_dersi", "dondurma", "iptal", "kisisel_antrenman"
                ],
                "responses_count": 45,
                "channels": ["website_widget", "whatsapp", "instagram_dm"],
                "tech_stack": ["Dialogflow", "WhatsApp Business API", "Node.js"],
                "estimated_hours": 25
            },
            "automation": {
                "workflows": [
                    {"name": "Devamsızlık Takip", "trigger": "No check-in 5 days", "action": "Motivation message"},
                    {"name": "Üyelik Yenileme", "trigger": "15 days before expiry", "action": "Renewal offer"},
                    {"name": "Yeni Üye Onboarding", "trigger": "New membership", "action": "Welcome + program"},
                    {"name": "Referans Programı", "trigger": "3 months active", "action": "Refer-a-friend offer"},
                    {"name": "Doğum Günü", "trigger": "Member birthday", "action": "Free PT session coupon"}
                ],
                "tech_stack": ["n8n", "WhatsApp Business API", "Google Sheets"],
                "estimated_hours": 20
            }
        },
        "auto_gallery": {
            "website": {
                "pages": ["Ana Sayfa", "Araç Listesi", "Araç Detay", "Değerleme", "Kredi", "İletişim"],
                "features": [
                    "Araç arama + filtreleme (marka, model, yıl, fiyat)",
                    "360° araç görüntüleme",
                    "Kredi hesaplayıcı",
                    "Araç değerleme formu",
                    "Sahibinden/Arabam entegrasyonu",
                    "WhatsApp ile sorgulama",
                    "Karşılaştırma özelliği",
                    "Stok yönetim paneli"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "PostgreSQL", "Cloudinary"],
                "estimated_hours": 50
            },
            "chatbot": {
                "intents": [
                    "arac_ara", "fiyat_sor", "kredi_hesapla", "test_surusu",
                    "takas", "degerle", "stok_sor", "konum"
                ],
                "responses_count": 55,
                "channels": ["website_widget", "whatsapp"],
                "tech_stack": ["Rasa", "WhatsApp Business API", "Python"],
                "estimated_hours": 30
            },
            "automation": {
                "workflows": [
                    {"name": "Yeni Araç Bildirimi", "trigger": "New car added", "action": "Notify interested buyers"},
                    {"name": "Fiyat Düşüşü", "trigger": "Price reduced", "action": "Alert watchers"},
                    {"name": "Takip", "trigger": "3 days after inquiry", "action": "Follow-up call reminder"},
                    {"name": "Sahibinden Sync", "trigger": "Daily", "action": "Auto-post new cars"},
                    {"name": "Satış Sonrası", "trigger": "After sale", "action": "Review request + referral"}
                ],
                "tech_stack": ["n8n", "Sahibinden API", "WhatsApp Business API"],
                "estimated_hours": 35
            }
        },
        "accounting": {
            "website": {
                "pages": ["Ana Sayfa", "Hizmetler", "Paketler", "Blog", "Müşteri Portalı", "İletişim"],
                "features": [
                    "Müşteri portalı (belge yükleme/indirme)",
                    "Hizmet paketleri + fiyatlandırma",
                    "Online randevu",
                    "Vergi takvimi widget",
                    "Blog + mevzuat güncellemeleri",
                    "Güvenli dosya paylaşımı",
                    "Fatura takip paneli",
                    "Responsive tasarım"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "Supabase", "AWS S3"],
                "estimated_hours": 40
            },
            "chatbot": {
                "intents": [
                    "hizmet_sor", "fiyat_bilgi", "belge_gonder", "vergi_takvimi",
                    "randevu_al", "fatura_sor", "mevzuat_bilgi", "acil_destek"
                ],
                "responses_count": 50,
                "channels": ["website_widget", "whatsapp"],
                "tech_stack": ["Dialogflow", "WhatsApp Business API", "Node.js"],
                "estimated_hours": 25
            },
            "automation": {
                "workflows": [
                    {"name": "Belge Toplama", "trigger": "Monthly cycle start", "action": "Request documents"},
                    {"name": "Vergi Hatırlatma", "trigger": "Tax deadline approaching", "action": "Client alert"},
                    {"name": "Fatura Takip", "trigger": "Invoice overdue", "action": "Reminder sequence"},
                    {"name": "Mevzuat Güncelleme", "trigger": "New regulation", "action": "Client briefing"},
                    {"name": "Yıllık Rapor", "trigger": "Year end", "action": "Annual summary to clients"}
                ],
                "tech_stack": ["n8n", "Google Workspace API", "WhatsApp Business API"],
                "estimated_hours": 25
            }
        },
        "construction": {
            "website": {
                "pages": ["Ana Sayfa", "Projeler", "Hizmetler", "Hakkımızda", "Galeri", "İletişim"],
                "features": [
                    "Proje portföyü + filtreleme",
                    "3D proje görselleştirme",
                    "Teklif talep formu",
                    "Proje ilerleme takibi (müşteri)",
                    "Referans projeleri",
                    "Sertifika ve belgeler",
                    "Video galeri",
                    "Responsive tasarım"
                ],
                "tech_stack": ["Next.js", "Tailwind CSS", "Supabase", "Three.js"],
                "estimated_hours": 50
            },
            "chatbot": {
                "intents": [
                    "teklif_al", "proje_bilgi", "referans_sor", "maliyet_tahmin",
                    "proje_takip", "malzeme_bilgi", "randevu_al", "garanti_bilgi"
                ],
                "responses_count": 45,
                "channels": ["website_widget", "whatsapp"],
                "tech_stack": ["Rasa", "WhatsApp Business API", "Python"],
                "estimated_hours": 30
            },
            "automation": {
                "workflows": [
                    {"name": "Teklif Takip", "trigger": "Proposal sent", "action": "Follow-up sequence"},
                    {"name": "Proje Güncelleme", "trigger": "Weekly", "action": "Client progress report"},
                    {"name": "Malzeme Sipariş", "trigger": "Stock low", "action": "Supplier notification"},
                    {"name": "Garanti Takip", "trigger": "Warranty period", "action": "Maintenance reminder"},
                    {"name": "Referans İsteme", "trigger": "Project completed", "action": "Review + referral request"}
                ],
                "tech_stack": ["n8n", "Google Workspace API", "Twilio"],
                "estimated_hours": 30
            }
        }
    }

    @classmethod
    def get_template(cls, sector: str, task_type: str) -> Dict:
        sector_data = cls.TEMPLATES.get(sector, {})
        return sector_data.get(task_type, {})

    @classmethod
    def get_full_project_spec(cls, sector: str) -> Dict:
        return cls.TEMPLATES.get(sector, {})

    @classmethod
    def estimate_total_hours(cls, sector: str) -> int:
        spec = cls.TEMPLATES.get(sector, {})
        return sum(t.get("estimated_hours", 0) for t in spec.values())


# ============================================
# CLAUDE CODE BRIDGE — Ana entegrasyon
# ============================================
class ClaudeCodeBridge:
    """JARVIS ↔ Claude Code köprüsü"""

    def __init__(self, projects_dir: str = "./projects"):
        self.projects_dir = projects_dir
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.templates = SectorTemplates()

    def create_project(self, customer_name: str, sector: str, package: str) -> Dict:
        """Yeni müşteri projesi oluştur"""
        project_id = hashlib.md5(f"{customer_name}{datetime.now()}".encode()).hexdigest()[:8]
        project_dir = f"{self.projects_dir}/{project_id}"

        spec = self.templates.get_full_project_spec(sector)
        total_hours = self.templates.estimate_total_hours(sector)

        # Paket bazlı scope belirleme
        scope = self._determine_scope(package, spec)

        project = {
            "project_id": project_id,
            "customer": customer_name,
            "sector": sector,
            "package": package,
            "directory": project_dir,
            "scope": scope,
            "total_estimated_hours": total_hours,
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "tasks": []
        }

        # Task'ları oluştur
        project["tasks"] = self._generate_tasks(project_id, scope, sector)

        return project

    def _determine_scope(self, package: str, spec: Dict) -> List[str]:
        """Paket bazlı scope"""
        if package == "Premium":
            return ["website", "chatbot", "automation"]
        elif package == "Professional":
            return ["website", "chatbot"]
        else:  # Starter
            return ["website"]

    def _generate_tasks(self, project_id: str, scope: List[str], sector: str) -> List[Dict]:
        """Claude Code için task listesi oluştur"""
        tasks = []
        task_num = 1

        for task_type in scope:
            template = self.templates.get_template(sector, task_type)
            if not template:
                continue

            if task_type == "website":
                # Website task'ları
                tasks.append({
                    "id": f"{project_id}-T{task_num:03d}",
                    "type": "website_setup",
                    "title": "Proje kurulumu + boilerplate",
                    "prompt": self._build_website_setup_prompt(sector, template),
                    "priority": TaskPriority.CRITICAL,
                    "status": TaskStatus.QUEUED,
                    "estimated_hours": 4
                })
                task_num += 1

                for page in template.get("pages", []):
                    tasks.append({
                        "id": f"{project_id}-T{task_num:03d}",
                        "type": "website_page",
                        "title": f"Sayfa: {page}",
                        "prompt": self._build_page_prompt(sector, page, template),
                        "priority": TaskPriority.HIGH,
                        "status": TaskStatus.QUEUED,
                        "estimated_hours": 5
                    })
                    task_num += 1

                for feature in template.get("features", []):
                    tasks.append({
                        "id": f"{project_id}-T{task_num:03d}",
                        "type": "website_feature",
                        "title": f"Özellik: {feature}",
                        "prompt": self._build_feature_prompt(sector, feature),
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.QUEUED,
                        "estimated_hours": 3
                    })
                    task_num += 1

            elif task_type == "chatbot":
                tasks.append({
                    "id": f"{project_id}-T{task_num:03d}",
                    "type": "chatbot_setup",
                    "title": "Chatbot altyapı kurulumu",
                    "prompt": self._build_chatbot_prompt(sector, template),
                    "priority": TaskPriority.HIGH,
                    "status": TaskStatus.QUEUED,
                    "estimated_hours": template.get("estimated_hours", 30)
                })
                task_num += 1

            elif task_type == "automation":
                for wf in template.get("workflows", []):
                    tasks.append({
                        "id": f"{project_id}-T{task_num:03d}",
                        "type": "automation_workflow",
                        "title": f"Otomasyon: {wf['name']}",
                        "prompt": self._build_automation_prompt(sector, wf),
                        "priority": TaskPriority.MEDIUM,
                        "status": TaskStatus.QUEUED,
                        "estimated_hours": 4
                    })
                    task_num += 1

        return tasks

    def _build_website_setup_prompt(self, sector: str, template: Dict) -> str:
        tech = ", ".join(template.get("tech_stack", []))
        return f"""Yeni bir {sector} sektörü web sitesi projesi kur.
Tech stack: {tech}
Sayfalar: {', '.join(template.get('pages', []))}
Responsive, SEO-friendly, Türkçe dil desteği.
Tailwind CSS ile modern, profesyonel tasarım.
Proje yapısını oluştur ve base layout'u hazırla."""

    def _build_page_prompt(self, sector: str, page: str, template: Dict) -> str:
        return f"""{sector} sektörü web sitesi için '{page}' sayfasını oluştur.
Modern, responsive tasarım. Tailwind CSS kullan.
Sektöre uygun içerik ve görseller için placeholder ekle.
SEO meta tagları ekle. Türkçe içerik."""

    def _build_feature_prompt(self, sector: str, feature: str) -> str:
        return f"""{sector} sektörü web sitesi için şu özelliği implement et: {feature}
Full-stack implementation. API endpoint + frontend component.
Error handling ve validation ekle. Türkçe UI."""

    def _build_chatbot_prompt(self, sector: str, template: Dict) -> str:
        intents = ", ".join(template.get("intents", []))
        channels = ", ".join(template.get("channels", []))
        return f"""{sector} sektörü için AI chatbot oluştur.
Intent'ler: {intents}
Kanallar: {channels}
Türkçe doğal dil anlama. Fallback mekanizması.
{template.get('responses_count', 50)} hazır yanıt şablonu."""

    def _build_automation_prompt(self, sector: str, workflow: Dict) -> str:
        return f"""{sector} sektörü için otomasyon workflow'u oluştur:
İsim: {workflow['name']}
Tetikleyici: {workflow['trigger']}
Aksiyon: {workflow['action']}
n8n/Make.com uyumlu. Error handling ekle."""

    def delegate_task(self, task: Dict) -> Dict:
        """Task'ı Claude Code'a delege et"""
        command = {
            "action": "execute",
            "task_id": task["id"],
            "prompt": task["prompt"],
            "working_directory": self.projects_dir,
            "timeout": 300,
            "auto_approve": task.get("priority") != TaskPriority.CRITICAL
        }

        # Claude Code CLI komutu
        cli_command = f'claude --print "{task["prompt"]}"'

        return {
            "task_id": task["id"],
            "command": command,
            "cli": cli_command,
            "status": "delegated",
            "delegated_at": datetime.now().isoformat()
        }

    def batch_delegate(self, tasks: List[Dict]) -> List[Dict]:
        """Birden fazla task'ı sırayla delege et"""
        results = []
        for task in tasks:
            result = self.delegate_task(task)
            results.append(result)
        return results

    def get_project_status(self, project: Dict) -> Dict:
        """Proje durumu özeti"""
        tasks = project.get("tasks", [])
        total = len(tasks)
        completed = sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in tasks if t["status"] == TaskStatus.IN_PROGRESS)

        return {
            "project_id": project["project_id"],
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "queued": total - completed - in_progress,
            "progress_percent": round(completed / total * 100) if total > 0 else 0,
            "estimated_remaining_hours": sum(
                t.get("estimated_hours", 0) for t in tasks 
                if t["status"] != TaskStatus.COMPLETED
            )
        }


# ============================================
# JARVIS ORCHESTRATOR — Tüm akışı yönetir
# ============================================
class JARVISOrchestrator:
    """JARVIS ana orkestratör — Lead'den Delivery'ye"""

    def __init__(self):
        self.bridge = ClaudeCodeBridge()
        self.active_projects: Dict[str, Dict] = {}

    def full_pipeline(self, lead_data: Dict, score_data: Dict) -> Dict:
        """Tam pipeline: Lead → Analiz → Teklif → Proje → Delivery"""

        business = lead_data.get("business_name", "")
        sector = lead_data.get("sector", "dental")
        package = score_data.get("package_recommendation", "Professional")

        # 1. Proje oluştur
        project = self.bridge.create_project(business, sector, package)
        self.active_projects[project["project_id"]] = project

        # 2. Task'ları hazırla
        tasks = project["tasks"]

        # 3. Proje durumu
        status = self.bridge.get_project_status(project)

        # 4. İlk task'ı delege et
        first_delegation = None
        if tasks:
            first_delegation = self.bridge.delegate_task(tasks[0])

        return {
            "project": {
                "id": project["project_id"],
                "customer": business,
                "sector": sector,
                "package": package
            },
            "status": status,
            "first_task": first_delegation,
            "total_tasks": len(tasks),
            "task_breakdown": {
                "website": sum(1 for t in tasks if "website" in t["type"]),
                "chatbot": sum(1 for t in tasks if "chatbot" in t["type"]),
                "automation": sum(1 for t in tasks if "automation" in t["type"])
            }
        }

    def get_delivery_timeline(self, sector: str, package: str) -> Dict:
        """Teslimat takvimi"""
        hours = SectorTemplates.estimate_total_hours(sector)
        scope = ["website"]
        if package in ["Professional", "Premium"]:
            scope.append("chatbot")
        if package == "Premium":
            scope.append("automation")

        # Scope'a göre saat hesapla
        spec = SectorTemplates.TEMPLATES.get(sector, {})
        total_hours = sum(spec.get(s, {}).get("estimated_hours", 0) for s in scope)

        # 6 saat/gün çalışma varsayımı
        working_days = math.ceil(total_hours / 6)

        timeline = {
            "sector": sector,
            "package": package,
            "scope": scope,
            "total_hours": total_hours,
            "working_days": working_days,
            "phases": []
        }

        day = 0
        for s in scope:
            template = spec.get(s, {})
            phase_hours = template.get("estimated_hours", 0)
            phase_days = math.ceil(phase_hours / 6)
            timeline["phases"].append({
                "phase": s,
                "start_day": day + 1,
                "end_day": day + phase_days,
                "hours": phase_hours,
                "days": phase_days
            })
            day += phase_days

        return timeline


# ============================================
# EXPORT
# ============================================
import math

if __name__ == "__main__":
    # Test
    bridge = ClaudeCodeBridge()
    project = bridge.create_project("İzmir Dentalizm", "dental", "Premium")
    print(f"Project: {project['project_id']}")
    print(f"Tasks: {len(project['tasks'])}")

    orchestrator = JARVISOrchestrator()
    timeline = orchestrator.get_delivery_timeline("dental", "Premium")
    print(f"Timeline: {timeline['working_days']} gün")
