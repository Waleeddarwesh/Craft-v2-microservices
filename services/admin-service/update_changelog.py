import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Handcrafts.settings')
django.setup()

from developer_portal.models import ChangelogEntry

ChangelogEntry.objects.all().delete()

v2_html = """
<p class="mb-4">Next-generation architectural evolution transitioning the monolithic backend into a distributed microservices ecosystem for isolated deployments, high availability, and infinite scalability.</p>

<h4 class="text-white font-bold text-lg mt-6 mb-3 flex items-center gap-2"><i class="ph ph-buildings"></i> Core System Capabilities</h4>
<ul class="list-disc pl-5 space-y-2 mb-6">
    <li><strong class="text-white">Multi-Vendor Marketplace & Logistics:</strong> Engineered a comprehensive e-commerce engine handling product variants, dynamic carts, Stripe payment orchestration, advanced return policies, and a dedicated delivery routing module for drivers.</li>
    <li><strong class="text-white">E-Learning Integration:</strong> Built a fully-featured digital academy allowing suppliers to upload video courses, track student enrollment progress, and issue automated certificates.</li>
    <li><strong class="text-white">Social & Engagement Engine:</strong> Developed a real-time social layer where users can follow suppliers, browse dynamic content feeds, and receive personalized product recommendations driven by an interaction-history algorithm (Views/Carts/Purchases).</li>
    <li><strong class="text-white">Real-Time Communication:</strong> Designed persistent, bi-directional WebSocket infrastructure using Django Channels and Redis for secure instant messaging and live push notifications (via Firebase Cloud Messaging).</li>
    <li><strong class="text-white">CRM & Conflict Resolution:</strong> Implemented a priority-based Support Ticket system and a multi-party Dispute Resolution workflow to mediate conflicts between buyers and suppliers safely.</li>
    <li><strong class="text-white">Automated Analytics & Reporting:</strong> Leveraged Celery and Celery Beat to offload heavy background processing, generating real-time supplier dashboards (total sales, return rates, top products) without blocking the main event loop.</li>
</ul>

<h4 class="text-white font-bold text-lg mt-6 mb-3 flex items-center gap-2"><i class="ph ph-shield-check"></i> Enterprise Security & DevOps Operations</h4>
<ul class="list-disc pl-5 space-y-2">
    <li><strong class="text-white">Granular Access Control:</strong> Engineered a complex Role-Based Access Control (RBAC) matrix defining strict permissions across four distinct interfaces: Customers, Suppliers, Delivery Personnel, and System Admins.</li>
    <li><strong class="text-white">Compliance & Hardening:</strong> Implemented strict GDPR data portability tools (JSON data export/soft delete), brute-force account lockout protection, Django AUTH_PASSWORD_VALIDATORS, and comprehensive Audit Logging for all admin actions.</li>
    <li><strong class="text-white">Cloud-Native Infrastructure:</strong> Fully containerized the stack using Docker & Docker Compose. Deployed on Railway utilizing Daphne ASGI with native HTTP/2 support, persistent PostgreSQL connection pooling, and dynamic, on-the-fly Arabic database translation using django-modeltranslation.</li>
</ul>
"""

entries = [
    {
        "version": "V2.0",
        "title": "Craft Microservices Evolution",
        "description": v2_html,
        "entry_type": "announcement",
        "date": datetime.date.today()
    },
    {
        "version": "V1.2",
        "title": "Advanced Backend Features",
        "description": "<p>Advanced backend features including audit logs, dispute resolution, support tickets, FCM push notifications, supplier analytics, and privacy-ready enhancements.</p>",
        "entry_type": "feature",
        "date": datetime.date.today() - datetime.timedelta(days=30)
    },
    {
        "version": "V1.1",
        "title": "Production-Ready Improvements",
        "description": "<p>Production-ready improvements including Docker, Daphne ASGI, Arabic localization, Redis, Celery, and CI/CD.</p>",
        "entry_type": "feature",
        "date": datetime.date.today() - datetime.timedelta(days=60)
    },
    {
        "version": "V1.0",
        "title": "Initial Architecture & MVP",
        "description": "<p>Initial architecture, core marketplace, supplier/customer/delivery roles, and e-learning MVP.</p>",
        "entry_type": "feature",
        "date": datetime.date.today() - datetime.timedelta(days=90)
    }
]

for entry in entries:
    obj = ChangelogEntry.objects.create(
        version=entry['version'],
        title=entry['title'],
        description=entry['description'],
        entry_type=entry['entry_type']
    )
    # Update date manually to bypass auto_now_add
    obj.published_date = entry['date']
    obj.save()

print("Changelogs created successfully with HTML!")
