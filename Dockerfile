# ১. পাইথনের অফিশিয়াল লাইটওয়েট ইমেজ ব্যবহার করা
FROM python:3.11-slim

# ২. কন্টেইনারের ভেতরে ওয়ার্কিং ডিরেক্টরি সেট করা
WORKDIR /app

# ৩. উইন্ডোজ বা ডকারের প্রয়োজনীয় কিছু সিস্টেম ডিপেন্ডেন্সি ইনস্টল করা
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ৪. ডিপেন্ডেন্সি ফাইল কপি এবং ইনস্টল করা
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ৫. প্রজেক্টের বাকি সব কোড ও ডাটাবেজ কন্টেইনারে কপি করা
COPY . .

# নিশ্চিত করুন ডকার রান করার আগে ডাটাবেজ অলরেডি পপুলেটেড আছে
RUN python -m database.mock_data

# ৬. Streamlit-এর ডিফল্ট পোর্ট ৮৫০১ এক্সপোজ করা
EXPOSE 8501

# 📊 কন্টেইনারের স্বাস্থ্য পরীক্ষার জন্য হেলথচেক (Production Best Practice)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 🚀 স্ট্রিমলিট অ্যাপটি রান করার ফাইনাল কমান্ড
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
