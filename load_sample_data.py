import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gate_prep.settings')
django.setup()

from django.contrib.auth.models import User
import argparse
from main.models import Subject, Topic, Article
from tests.models import MockTest, Question

def load_sample_data():
    # Create subjects
    subjects_data = [
        {'name': 'Mine Planning & Design', 'description': 'Comprehensive coverage of mine planning, design principles, and optimization techniques.'},
        {'name': 'Rock Mechanics', 'description': 'Study of rock behavior, stress analysis, and ground control methods.'},
        {'name': 'Mine Ventilation', 'description': 'Ventilation systems, air flow analysis, and environmental control in mines.'},
        {'name': 'Mineral Processing', 'description': 'Ore processing, beneficiation techniques, and metallurgical processes.'},
        {'name': 'Mining Machinery', 'description': 'Equipment selection, maintenance, and operational efficiency in mining.'},
        {'name': 'Mine Safety', 'description': 'Safety protocols, hazard identification, and risk management in mining operations.'}
    ]
    
    subjects = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            defaults={'description': subject_data['description']}
        )
        subjects.append(subject)
        if created:
            print(f"Created subject: {subject.name}")
    
    # Create topics for each subject
    topics_data = {
        'Mine Planning & Design': [
            'Surface Mine Planning', 'Underground Mine Design', 'Ore Reserve Estimation',
            'Mine Layout Optimization', 'Production Scheduling'
        ],
        'Rock Mechanics': [
            'Stress Analysis', 'Rock Properties', 'Ground Support Systems',
            'Slope Stability', 'Underground Excavations'
        ],
        'Mine Ventilation': [
            'Ventilation Networks', 'Fan Selection', 'Air Quality Control',
            'Methane Management', 'Dust Control'
        ],
        'Mineral Processing': [
            'Crushing & Grinding', 'Flotation', 'Gravity Separation',
            'Magnetic Separation', 'Hydrometallurgy'
        ],
        'Mining Machinery': [
            'Excavation Equipment', 'Material Handling', 'Drilling Systems',
            'Conveyor Systems', 'Maintenance Planning'
        ],
        'Mine Safety': [
            'Hazard Assessment', 'Emergency Procedures', 'Personal Protective Equipment',
            'Gas Monitoring', 'Accident Prevention'
        ]
    }
    
    topics = []
    for subject in subjects:
        if subject.name in topics_data:
            for topic_name in topics_data[subject.name]:
                topic, created = Topic.objects.get_or_create(
                    subject=subject,
                    name=topic_name,
                    defaults={'description': f'Detailed study of {topic_name} in {subject.name}'}
                )
                topics.append(topic)
                if created:
                    print(f"Created topic: {topic.name}")
    
    # Determine author user to assign articles to
    def get_or_create_author(preferred_username=None):
        candidates = []
        if preferred_username:
            candidates.append(preferred_username)
        # sensible fallbacks
        candidates += ['vinod', 'admin', 'superuser', 'root']

        for uname in candidates:
            u = User.objects.filter(username=uname).first()
            if u:
                print(f"Using existing user: {uname}")
                return u

        # if none found, create a seed user with an unusable password
        create_name = preferred_username or 'seeduser'
        user, created = User.objects.get_or_create(
            username=create_name,
            defaults={'email': f'{create_name}@example.com'}
        )
        if created:
            user.set_unusable_password()
            user.is_staff = False
            user.save()
            print(f"Created seed user: {create_name} (unusable password)")
        else:
            print(f"Using existing fallback user: {create_name}")
        return user

    # parse optional CLI arg --user
    parser = argparse.ArgumentParser(description='Load sample data into the project DB')
    parser.add_argument('--user', help='Username to assign as article author', default=None)
    args, unknown = parser.parse_known_args()
    admin_user = get_or_create_author(args.user)
    
    articles_data = [
        {
            'title': 'Introduction to Surface Mine Planning',
            'slug': 'intro-surface-mine-planning',
            'content': '''Surface mine planning is a critical aspect of mining engineering that involves the systematic design and optimization of open-pit mining operations. This comprehensive guide covers the fundamental principles and methodologies used in modern surface mining.

## Key Components of Surface Mine Planning

### 1. Geological Assessment
The foundation of any successful surface mining operation begins with a thorough geological assessment. This involves:
- Detailed geological mapping and sampling
- Ore body delineation and characterization
- Geotechnical analysis of rock formations
- Environmental impact assessment

### 2. Economic Evaluation
Economic viability is crucial for mine planning decisions:
- Net Present Value (NPV) calculations
- Internal Rate of Return (IRR) analysis
- Sensitivity analysis for commodity prices
- Operating cost estimation

### 3. Mine Design Optimization
Modern mine planning utilizes advanced software tools for:
- Pit optimization algorithms
- Production scheduling
- Equipment selection and sizing
- Waste dump planning

## Planning Methodologies

### Lerchs-Grossmann Algorithm
The Lerchs-Grossmann algorithm is widely used for determining the ultimate pit limits that maximize the net present value of the mining operation.

### Production Scheduling
Effective production scheduling ensures:
- Optimal ore and waste extraction sequences
- Equipment utilization maximization
- Grade control and blending strategies
- Environmental compliance

## Best Practices

1. **Integrated Planning Approach**: Consider all aspects simultaneously
2. **Risk Assessment**: Evaluate geological, technical, and economic risks
3. **Sustainability**: Incorporate environmental and social considerations
4. **Technology Integration**: Utilize modern planning software and automation

This article provides the foundation for understanding surface mine planning principles that are essential for GATE Mining Engineering preparation.''',
            'excerpt': 'Comprehensive guide to surface mine planning covering geological assessment, economic evaluation, and optimization techniques.',
            'difficulty': 'medium'
        },
        {
            'title': 'Rock Mechanics Fundamentals',
            'slug': 'rock-mechanics-fundamentals',
            'content': '''Rock mechanics is the theoretical and applied science of the mechanical behavior of rock masses. Understanding rock mechanics is essential for safe and efficient mining operations.

## Stress and Strain in Rocks

### Principal Stresses
Rock masses are subjected to three principal stresses:
- σ₁ (Maximum principal stress)
- σ₂ (Intermediate principal stress)  
- σ₃ (Minimum principal stress)

### Mohr-Coulomb Failure Criterion
The Mohr-Coulomb criterion is fundamental for predicting rock failure:
τ = c + σₙ tan φ

Where:
- τ = Shear stress at failure
- c = Cohesion
- σₙ = Normal stress
- φ = Angle of internal friction

## Rock Properties

### Strength Properties
- Uniaxial Compressive Strength (UCS)
- Tensile Strength
- Shear Strength
- Triaxial Strength

### Deformation Properties
- Young's Modulus (E)
- Poisson's Ratio (ν)
- Bulk Modulus (K)
- Shear Modulus (G)

## Ground Support Systems

### Support Types
1. **Active Support**: Pre-stressed systems (rock bolts, cables)
2. **Passive Support**: Load-responsive systems (timber, steel sets)
3. **Surface Support**: Mesh, shotcrete, steel plates

### Design Considerations
- Rock mass classification (RMR, Q-system)
- Excavation geometry and orientation
- In-situ stress conditions
- Time-dependent behavior

## Applications in Mining

### Underground Excavations
- Tunnel stability analysis
- Pillar design and sizing
- Stope stability assessment
- Support system selection

### Surface Mining
- Slope stability analysis
- Bench design optimization
- Waste dump stability
- Highwall monitoring

Understanding these fundamental concepts is crucial for solving rock mechanics problems in the GATE Mining Engineering examination.''',
            'excerpt': 'Essential concepts in rock mechanics including stress analysis, rock properties, and ground support systems for mining applications.',
            'difficulty': 'hard'
        },
        {
            'title': 'Mine Ventilation Systems',
            'slug': 'mine-ventilation-systems',
            'content': '''Mine ventilation is critical for maintaining safe working conditions in underground mines. This article covers the fundamental principles and design considerations for effective ventilation systems.

## Ventilation Objectives

### Primary Goals
1. **Air Quality Control**: Maintain breathable atmosphere
2. **Temperature Control**: Regulate underground temperatures
3. **Humidity Control**: Manage moisture levels
4. **Contaminant Removal**: Eliminate harmful gases and dust

### Regulatory Requirements
- Minimum air velocity standards
- Air quality parameters (O₂, CO₂, CO, CH₄)
- Temperature and humidity limits
- Dust concentration thresholds

## Ventilation Networks

### Network Components
- **Airways**: Tunnels, shafts, and drifts
- **Fans**: Main, booster, and auxiliary fans
- **Regulators**: Doors, stopping, and dampers
- **Air Courses**: Intake and return airways

### Airflow Principles
The fundamental equation for airflow in mine ventilation:
Q = A × V

Where:
- Q = Air quantity (m³/s)
- A = Cross-sectional area (m²)
- V = Air velocity (m/s)

## Fan Selection and Design

### Fan Types
1. **Centrifugal Fans**: High pressure applications
2. **Axial Fans**: High volume, low pressure
3. **Mixed Flow Fans**: Combination characteristics

### Fan Laws
- Q₁/Q₂ = (N₁/N₂) × (D₁/D₂)³
- H₁/H₂ = (N₁/N₂)² × (D₁/D₂)²
- P₁/P₂ = (N₁/N₂)³ × (D₁/D₂)⁵

## Ventilation Planning

### Design Process
1. **Airway Layout**: Plan intake and return routes
2. **Quantity Calculations**: Determine required airflow
3. **Pressure Analysis**: Calculate system resistance
4. **Fan Selection**: Choose appropriate equipment
5. **Control Systems**: Design regulation methods

### Special Considerations
- **Methane Drainage**: Gas capture and removal
- **Dust Suppression**: Water sprays and collectors
- **Emergency Ventilation**: Escape route planning
- **Energy Efficiency**: Optimize power consumption

## Monitoring and Control

### Monitoring Systems
- Continuous gas monitoring
- Airflow measurement stations
- Temperature and humidity sensors
- Dust concentration monitors

### Control Strategies
- Automatic fan control systems
- Remote monitoring capabilities
- Emergency response protocols
- Maintenance scheduling

Proper ventilation system design is essential for safe mining operations and is a key topic in GATE Mining Engineering examinations.''',
            'excerpt': 'Complete guide to mine ventilation systems covering airflow principles, fan selection, and safety considerations.',
            'difficulty': 'medium'
        }
    ]
    
    for i, article_data in enumerate(articles_data):
        # Get appropriate topic
        topic = topics[i] if i < len(topics) else topics[0]
        
        article, created = Article.objects.get_or_create(
            slug=article_data['slug'],
            defaults={
                'title': article_data['title'],
                'content': article_data['content'],
                'excerpt': article_data['excerpt'],
                'topic': topic,
                'difficulty': article_data['difficulty'],
                'author': admin_user,
                'is_published': True
            }
        )
        if created:
            print(f"Created article: {article.title}")
    
    # Create sample mock tests
    for subject in subjects[:3]:  # Create tests for first 3 subjects
        test, created = MockTest.objects.get_or_create(
            title=f"{subject.name} - Practice Test",
            defaults={
                'description': f'Comprehensive practice test covering key concepts in {subject.name}',
                'subject': subject,
                'difficulty': 'medium',
                'duration_minutes': 60,
                'total_marks': 100,
                'is_active': True,
                'is_featured': True
            }
        )
        
        if created:
            print(f"Created test: {test.title}")
            
            # Add sample questions
            subject_topics = Topic.objects.filter(subject=subject)[:3]
            for j, topic in enumerate(subject_topics):
                # MCQ Question
                Question.objects.get_or_create(
                    mock_test=test,
                    topic=topic,
                    question_text=f"What is the most important factor in {topic.name.lower()}?",
                    defaults={
                        'question_type': 'mcq',
                        'options': {
                            'A': 'Safety considerations',
                            'B': 'Economic factors',
                            'C': 'Technical feasibility',
                            'D': 'Environmental impact'
                        },
                        'correct_answer': 'A',
                        'explanation': f'Safety is always the primary consideration in {topic.name.lower()}.',
                        'marks': 2,
                        'difficulty': 'medium'
                    }
                )
                
                # Numerical Question
                Question.objects.get_or_create(
                    mock_test=test,
                    topic=topic,
                    question_text=f"Calculate the efficiency factor for {topic.name.lower()} given standard parameters.",
                    defaults={
                        'question_type': 'numerical',
                        'correct_answer': '0.85',
                        'explanation': f'The standard efficiency factor for {topic.name.lower()} is typically 0.85.',
                        'marks': 3,
                        'difficulty': 'hard'
                    }
                )

if __name__ == '__main__':
    load_sample_data()
    print("Sample data loaded successfully!")