# Cognitive Mirror

Cognitive Mirror is a web-based tool for analyzing online text.  
It combines machine learning models to detect:  

- **Russian Propaganda** — binary classification (propaganda / non-propaganda), trained on content related to the Russo-Ukrainian war  
- **Manipulation techniques** such as *slippery slope*, *appeal to majority*, *false dilemma*, etc.  
- **Emotions expressed in text**, based on a state-of-the-art emotion classification model  

While the propaganda detector is trained on war-related content, the **manipulation detection** and **emotion classification** modules can be applied to texts on any topic.


---

## Live Demo
The project is stable and freely accessible via the website:  
👉 [cognitive--mirror.com](https://cognitive--mirror.com/)

Screenshots highlighting the features of our website:

![Screenshot placeholder](assets/Cognitive%20Mirror%20Screenshot%203.png)  

![Screenshot placeholder](assets/Cognitive%20Mirror%20Screenshot%202.png)  

![Screenshot placeholder](assets/Cognitive%20Mirror%20Screenshot%201.png)

---

## Technology Overview

Cognitive Mirror is powered by three transformer-based models:

1. **Russian Propaganda Detection**  
   - Model: fine-tuned BERTweet transformer  
   - Dataset used: [HQP: A Human-Annotated Dataset for Detecting Online Propaganda](https://aclanthology.org/2024.findings-acl.363.pdf)  
   - Dataset's GitHub: [HiQualProp](https://github.com/abdumaa/HiQualProp/tree/main)  

2. **Manipulation Technique Detection**  
   - Model: fine-tuned BERTweet transformer  
   - Dataset used: [COCOLOFA: A Dataset of News Comments with Common Logical Fallacies](https://arxiv.org/pdf/2410.03457v1)  
   - Dataset's GitHub: [COCOLOFA repository](https://github.com/Crowd-AI-Lab/cocolofa/tree/main)  

3. **Emotion Classification**  
   - Model: [GoEmotions (monologg/bert-base-cased-goemotions-original)](https://huggingface.co/monologg/bert-base-cased-goemotions-original)  

**Backend:** [FastAPI](https://fastapi.tiangolo.com/)  
**Frontend:** [NiceGUI](https://nicegui.io/)  

---

## Features
- Detects Russian propaganda in online text  
- Identifies logical fallacies and manipulation techniques  
- Classifies emotions to better understand user sentiment  
- Web-based — no installation required  

---

## Contributing

We welcome contributions! You can help by:
- Reporting bugs or suggesting new features  
- Sharing additional datasets related to Russian propaganda or logical fallacies used in text  

For feedback or collaboration, contact us at:  
 **buymerivka@gmail.com**

---

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file in this repository for details.

---

## 👥 Authors

- **Arsenii Galaida**  
  [LinkedIn](https://www.linkedin.com/in/arsenii-galaida/) • [GitHub](https://github.com/ArseniiGalaida)  

- **Yehor Kuzmych**  
  [LinkedIn](https://www.linkedin.com/in/yehor-kuzmych-b78453353/) • [GitHub](https://github.com/yehor-kuzmych)  

---

