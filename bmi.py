berat = float(input("Masukkan berat badan (kg): "))
tinggi = float(input("Masukkan tinggi badan (cm): "))

tinggi_m = tinggi / 100
bmi = berat / (tinggi_m ** 2)

if bmi < 18.5:
    kategori = "Underweight"
elif bmi <= 24.9:
    kategori = "Normal"
elif bmi <= 29.9:
    kategori = "Overweight"
else:
    kategori = "Obesity"

print(f"Nilai BMI: {bmi:.2f}")
print(f"Kategori: {kategori}")
