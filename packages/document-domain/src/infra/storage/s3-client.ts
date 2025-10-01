import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import pino from 'pino';

const logger = pino({ name: 's3-client' });

const s3Client = new S3Client({
  endpoint: process.env.STORAGE_ENDPOINT || 'http://localhost:9000',
  region: process.env.STORAGE_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.STORAGE_ACCESS_KEY || 'minioadmin',
    secretAccessKey: process.env.STORAGE_SECRET_KEY || 'minioadmin',
  },
  forcePathStyle: true,
});

const BUCKET = process.env.STORAGE_BUCKET || 'valero-docs';

export async function uploadToS3(key: string, buffer: Buffer, contentType: string): Promise<string> {
  logger.debug({ key, size: buffer.length }, 'Uploading to S3');

  await s3Client.send(new PutObjectCommand({
    Bucket: BUCKET,
    Key: key,
    Body: buffer,
    ContentType: contentType,
  }));

  return `s3://${BUCKET}/${key}`;
}

export async function generateSignedUrl(uri: string, expiresIn: number = 3600): Promise<string> {
  const key = uri.replace(`s3://${BUCKET}/`, '');
  
  const command = new GetObjectCommand({
    Bucket: BUCKET,
    Key: key,
  });

  return await getSignedUrl(s3Client, command, { expiresIn });
}
