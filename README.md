# مستندات فیلترهای API فروشگاه

در این بخش، فیلترهای قابل استفاده برای هر مدل و نحوه استفاده از آن‌ها در URL آورده شده است.

---

## فیلترهای محصولات (Product)

### فیلترهای پایه
- **جستجو**:  
  `/api/products/?search=لپ‌تاپ`
- **فعال بودن**:  
  `/api/products/?is_active=true`
- **موجودی**:  
  `/api/products/?in_stock=true`

### فیلترهای چندتایی (Multiple Choice)
- **دسته‌بندی‌ها**:  
  `/api/products/?categories=1,2,3`
- **برندها**:  
  `/api/products/?brands=1,2`
- **تگ‌ها**:  
  `/api/products/?tags=1,2,3`
- **رنگ‌ها**:  
  `/api/products/?colors=1,2`
- **گارانتی‌ها**:  
  `/api/products/?warranties=1,2`
- **گروه‌های مشخصات**:  
  `/api/products/?spec_groups=1,2,3`

### فیلترهای محدوده‌ای (Range)
- **محدوده قیمت**:  
  `/api/products/?price_range_min=1000000&price_range_max=5000000`

### فیلترهای بولی (Boolean)
- **دارای تخفیف**:  
  `/api/products/?has_discount=true`
- **دارای گارانتی**:  
  `/api/products/?has_warranty=true`

### فیلترهای مشخصات فنی
- **مشخصات فنی (نام:مقدار)**:  
  `/api/products/?specification=RAM:8GB`  
  `/api/products/?specification=رنگ:قرمز`
- **مشخصات فنی (نام:حداقل:حداکثر)**:  
  `/api/products/?specification=Storage:128:512`
- **مشخصات فنی چندتایی**:  
  `/api/products/?specification=رنگ:قرمز,آبی,سبز`
- **مشخصات فنی (آیدی مقدار)**:  
  `/api/products/?spec_by_id=128,512`
- **مشخصات فنی (آیدی)**:  
  `/api/products/?spec_ids=5,10,15`
- **مقادیر مشخصات فنی (آیدی)**:  
  `/api/products/?spec_value_ids=12,14,15`

---

## فیلترهای دسته‌بندی (Category)

| نام فیلتر                | فرمت/مثال                                         | توضیحات کوتاه                        |
|-------------------------|---------------------------------------------------|--------------------------------------|
| جستجو                   | `/api/categories/?search=تبلت`                    | جستجو بر اساس نام یا توضیحات         |
| والد                    | `/api/categories/?parent=30`                      | فیلتر بر اساس آیدی والد              |
| فعال بودن               | `/api/categories/?is_active=true`                  | فقط دسته‌های فعال                    |
| برندها                  | `/api/categories/?brands=30,31`                   | چند برند با ویرگول                   |
| گروه مشخصات             | `/api/categories/?spec_group=1,2`                 | چند گروه مشخصات                      |
| مشخصات فنی (آیدی)       | `/api/categories/?spec_definitions=109,110`       | چند مشخصه فنی                        |
| نام مشخصه               | `/api/categories/?spec_names=RAM`                 | جستجو در نام مشخصه                   |
| مقدار عددی مشخصه        | `/api/categories/?spec_int_value=8`               | مقدار عددی                           |
| مقدار اعشاری مشخصه      | `/api/categories/?spec_decimal_value=12.9`        | مقدار اعشاری                         |
| مقدار متنی مشخصه        | `/api/categories/?spec_str_value=قرمز`            | مقدار متنی                            |
| مقدار بله/خیر مشخصه     | `/api/categories/?spec_bool_value=true`           | مقدار بولی                            |
| مقدار مشخصه (پیشرفته)   | `/api/categories/?spec_value=151,150`     | فیلتر بر اساس آیدی مقدار ProductSpecification |

> ⚠️ **نکته مهم:**
> برای استفاده از فیلتر `spec_value` یا `spec_by_id` فقط کافی است آیدی مقدار مشخصه محصول (ProductSpecification) را از داده‌های واقعی یا دیتابیس پیدا کنی. مثال:
> - 151 یعنی مقدار ProductSpecification id=151 (مثلاً مقدارش 8 است)
> - 150 یعنی مقدار ProductSpecification id=150 (مثلاً مقدارش 512 است)
> اگر چند مقدار داری، همه آیدی‌ها را با ویرگول جدا کن: `/api/categories/?spec_value=151,152,150,153` یا `/api/products/?spec_by_id=128,512,700`

---

## فیلترهای ویژگی محصول (ProductOption)

### فیلترهای پایه
- **جستجو**:  
  `/api/product-options/?search=لپ‌تاپ`
- **محصول**:  
  `/api/product-options/?product=1`
- **رنگ**:  
  `/api/product-options/?color=1`
- **گارانتی**:  
  `/api/product-options/?warranty=1`
- **فعال بودن**:  
  `/api/product-options/?is_active=true`

### فیلترهای محدوده‌ای
- **محدوده قیمت**:  
  `/api/product-options/?price_range_min=1000000&price_range_max=5000000`
- **محدوده تخفیف**:  
  `/api/product-options/?discount_range_min=10&discount_range_max=50`

### فیلترهای بولی
- **دارای گارانتی**:  
  `/api/product-options/?has_warranty=true`
- **دارای تخفیف**:  
  `/api/product-options/?has_discount=true`
- **تخفیف فعال**:  
  `/api/product-options/?is_active_discount=true`

---

## فیلترهای گارانتی (Warranty)

### فیلترهای پایه
- **جستجو**:  
  `/api/warranties/?search=شرکت`
- **نام شرکت**:  
  `/api/warranties/?company=شرکت گارانتی`
- **فعال بودن**:  
  `/api/warranties/?is_active=true`
- **نیاز به ثبت**:  
  `/api/warranties/?registration_required=true`

### فیلترهای محدوده‌ای
- **محدوده مدت**:  
  `/api/warranties/?duration_range_min=12&duration_range_max=36`

### فیلترهای بولی
- **دارای محصول**:  
  `/api/warranties/?has_product_options=true`

---

## فیلترهای گروه مشخصات (SpecificationGroup)

### فیلترهای پایه
- **جستجو**:  
  `/api/specification-groups/?search=ظاهری`

### فیلترهای بولی
- **دارای مشخصات**:  
  `/api/specification-groups/?has_specifications=true`

---

## فیلترهای مشخصات فنی (Specification)

### فیلترهای پایه
- **جستجو**:  
  `/api/specifications/?search=RAM`
- **نوع داده**:  
  `/api/specifications/?data_type=int`
- **نام**:  
  `/api/specifications/?name=RAM`
- **اصلی بودن**:  
  `/api/specifications/?is_main=true`

### فیلترهای چندتایی
- **دسته‌بندی‌ها**:  
  `/api/specifications/?categories=1,2`
- **گروه**:  
  `/api/specifications/?group=1`

---

## نحوه ترکیب فیلترها

شما می‌توانید چندین فیلتر را همزمان استفاده کنید:

```
GET /api/products/?categories=1,2&brands=1&price_range_min=1000000&has_discount=true&spec_groups=1,2&specification=RAM:8GB
```

### مثال‌های کاربردی

#### 1. محصولات لپ‌تاپ با RAM 8GB و قیمت بین 2 تا 5 میلیون:
```
GET /api/products/?categories=1&specification=RAM:8&price_range_min=2000000&price_range_max=5000000
```
#### 1.1. محصولات لپ‌تاپ با RAM 8GB (با آیدی مقدار):
```
GET /api/products/?categories=1&spec_by_id=128&price_range_min=2000000&price_range_max=5000000
```

#### 1.2. محصولات با مقادیر مشخصات فنی خاص (با آیدی مقدار):
```
GET /api/products/?spec_value_ids=12,14,15
```

#### 2. محصولات دارای تخفیف در گروه مشخصات ظاهری:
```
GET /api/products/?has_discount=true&spec_groups=1
```

#### 3. محصولات برند خاص با رنگ‌های مختلف:
```
GET /api/products/?brands=1&colors=1,2,3
```

#### 4. محصولات فعال با گارانتی:
```
GET /api/products/?is_active=true&has_warranty=true
```

---

## نکات مهم

### فرمت‌های فیلتر

1. **فیلترهای چندتایی**: مقادیر را با کاما جدا کنید
   ```
   ?categories=1,2,3
   ```

2. **فیلترهای محدوده‌ای**: از دو پارامتر min و max استفاده کنید
   ```
   ?price_range_min=1000000&price_range_max=5000000
   ```

3. **فیلتر مشخصات فنی**: فرمت `نام:مقدار` یا `نام:حداقل:حداکثر`
   ```
   ?specification=RAM:8GB
   ?specification=Storage:128:512
   ```
4. **فیلتر مشخصات فنی با آیدی**: فرمت `آیدی:مقدار` یا `آیدی:حداقل:حداکثر`
   ```
   ?spec_by_id=5:8GB
   ?spec_by_id=10:128:512
   ```
5. **فیلتر آیدی مشخصات**: مقادیر را با کاما جدا کنید
   ```
   ?spec_ids=5,10,15
   ```
6. **فیلتر آیدی مقادیر مشخصات فنی**: مقادیر را با کاما جدا کنید
   ```
   ?spec_value_ids=12,14,15
   ```

4. **فیلترهای بولی**: از `true` یا `false` استفاده کنید
   ```
   ?is_active=true
   ?has_discount=false
   ```

### کدهای خطا

- **400 Bad Request**: پارامترهای فیلتر نامعتبر
- **404 Not Found**: آیدی‌های ارسالی وجود ندارند
- **500 Internal Server Error**: خطای سرور

### محدودیت‌ها

- حداکثر 100 محصول در هر درخواست
- حداکثر 10 فیلتر همزمان
- فیلترهای متنی حساس به حروف کوچک و بزرگ نیستند
- فیلترهای عددی فقط اعداد صحیح و اعشاری را می‌پذیرند

---

## تست فیلترها

برای تست فیلترها می‌توانید از ابزارهای زیر استفاده کنید:

1. **Postman**: برای تست API
2. **cURL**: برای تست از خط فرمان
3. **مرورگر**: برای تست فیلترهای ساده

### مثال cURL:
```bash
curl "http://localhost:8000/api/products/?categories=1,2&brands=1&has_discount=true"
``` 