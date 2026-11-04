# Supabase Setup Guide for CoconutSMP

This guide will help you set up Supabase for image storage while keeping Firebase for everything else.

## 🎯 Architecture

- **Firebase**: Forms, Chat, Player Data, Real-time sync
- **Supabase**: Image storage only

## 📦 Supabase Configuration

Your current Supabase config:
```
URL: https://qnhxebwjzifnjlfgcuxu.supabase.co
Key: sb_publishable_xgSNVLfCl1scznE2HIZwWg_va6P7KUe
```

## 🔧 Step 1: Create Storage Bucket

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `qnhxebwjzifnjlfgcuxu`
3. Navigate to **Storage** on the left sidebar
4. Click **"New Bucket"**
5. Bucket name: `images`
6. Make bucket **Public** (important for images to be accessible)
7. Click **"Create Bucket"**

## 🔐 Step 2: Configure Bucket Policies

### Option A: Make Bucket Public (Recommended for Images)

1. In the Storage section, click on the `images` bucket
2. Click **"Policies"** tab
3. Click **"New Policy"**
4. Select **"For full customization"**
5. Name: `Public Access`
6. Use this policy:

```sql
-- Allow public read access
CREATE POLICY "Public Read Access"
ON storage.objects
FOR SELECT
TO public
USING ( bucket_id = 'images' );

-- Allow authenticated uploads
CREATE POLICY "Authenticated Upload"
ON storage.objects
FOR INSERT
TO public
WITH CHECK ( bucket_id = 'images' );

-- Allow authenticated deletions
CREATE POLICY "Authenticated Delete"
ON storage.objects
FOR DELETE
TO public
USING ( bucket_id = 'images' );
```

### Option B: Using the Supabase Dashboard UI

1. In Storage → images bucket
2. Click **"Policies"**
3. Click **"New Policy"** → **"Get started quickly"**
4. Select **"Public Read Access"** template
5. Enable: **SELECT** operations
6. Target: **All tables** (or specific to your needs)
7. Click **"Save"**

## 📁 Step 3: Create Folders (Optional)

1. In the `images` bucket, create a folder called `uploads`
2. This keeps uploaded images organized

## 🎨 Step 4: Configure Image Transformation (Optional)

Supabase supports image transformation. You can resize, crop, and optimize images on the fly:

```javascript
// Example: Get resized image
const { data } = supabase.storage
  .from('images')
  .getPublicUrl('uploads/image.jpg', {
    transform: {
      width: 800,
      height: 600,
      quality: 80
    }
  });
```

## 🔒 Step 5: Row Level Security (Optional but Recommended)

For better security, enable RLS on your storage:

```sql
-- Enable RLS
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy for reading
CREATE POLICY "Allow Public Read"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'images');

-- Policy for uploading
CREATE POLICY "Allow Upload"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'images' AND auth.role() = 'authenticated');

-- Policy for deleting
CREATE POLICY "Allow Delete"
ON storage.objects
FOR DELETE
TO public
USING (bucket_id = 'images' AND auth.role() = 'authenticated');
```

## 📊 Step 6: Storage Limits (Free Tier)

Supabase Free Tier includes:
- **1 GB** database storage
- **1 GB** file storage
- **2 GB** bandwidth per month
- **50,000** MAU (Monthly Active Users)

If you need more, paid plans start at $25/month.

## 🧪 Step 7: Test the Setup

1. Open the dashboard: `http://localhost:8080/dashboard.html`
2. Scroll to "Image Upload (Supabase)" section
3. Select an image file
4. Click "Upload to Supabase"
5. Check if the image appears in the gallery below
6. Verify the image URL works by clicking "View"

## 🐛 Troubleshooting

### "Bucket not found" error
- Make sure you created the `images` bucket
- Check the bucket name is exactly `images` (case-sensitive)

### "Permission denied" error
- Check your storage policies
- Ensure the bucket is public or policies allow access
- Verify your Supabase URL and key are correct

### Images not loading in gallery
- Check browser console for errors
- Verify the bucket is public
- Check if images actually uploaded to Supabase
- Try refreshing the images

### "Supabase not initialized" error
- Check if Supabase SDK loaded correctly
- Verify the URL and key in dashboard.html
- Check browser console for initialization errors

## 📝 File Upload Code

The dashboard uses this code to upload images:

```javascript
async function uploadImage() {
    const file = fileInput.files[0];
    const fileName = nameInput.value || `${Date.now()}_${file.name}`;
    const filePath = `uploads/${fileName}`;

    const { data, error } = await supabase.storage
        .from('images')
        .upload(filePath, file);

    if (error) throw error;

    const { data: { publicUrl } } = supabase.storage
        .from('images')
        .getPublicUrl(filePath);

    return publicUrl;
}
```

## 🎯 Best Practices

1. **Image Optimization**: Compress images before uploading
2. **File Size Limits**: Consider adding client-side size limits
3. **File Type Validation**: Only allow image types (jpg, png, webp, gif)
4. **Naming**: Use unique names to avoid conflicts
5. **Organization**: Use folders to organize images by type/date
6. **Cleanup**: Regularly delete unused images to save storage

## 🔗 Integration with Forms

To add image uploads to forms (e.g., bug report screenshots):

```javascript
// In forms.html, add image upload input
<input type="file" id="evidence-image" accept="image/*">

// In submitForm function, upload image first
const imageFile = document.getElementById('evidence-image').files[0];
if (imageFile && supabase) {
    const { data, error } = await supabase.storage
        .from('images')
        .upload(`evidence/${Date.now()}_${imageFile.name}`, imageFile);
    
    if (!error) {
        formData.evidenceImage = data.path;
    }
}
```

## 📚 Additional Resources

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [Storage Policies Guide](https://supabase.com/docs/guides/storage/security/access-control)

## ✅ Checklist

- [ ] Created `images` bucket in Supabase
- [ ] Made bucket public or configured policies
- [ ] Created `uploads` folder (optional)
- [ ] Tested image upload from dashboard
- [ ] Verified images appear in gallery
- [ ] Checked image URLs are accessible
- [ ] Reviewed storage limits
- [ ] Configured image transformation (optional)

## 🎉 Next Steps

Once Supabase is set up:
1. Upload test images
2. Integrate image uploads into forms
3. Add image validation
4. Set up automated cleanup of old images
5. Consider adding image thumbnails

## 🔥 Firebase vs Supabase Reminder

- **Firebase**: Forms, Chat, Player Data, Real-time
- **Supabase**: Images only

This hybrid approach gives you the best of both worlds!
