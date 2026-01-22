# AWS Icons in Langflow Components

## Current Implementation

Langflow uses **Lucide icons** by default. Our components use the best matching Lucide icons for AWS services:

| AWS Service | Lucide Icon | Notes |
|------------|-------------|-------|
| VPC | `network` | Represents networking infrastructure |
| ECS Cluster | `server` | Represents compute cluster |
| ECS Service | `container` | Represents containerized service |
| ALB | `scale` | Represents load balancing |
| Security Group | `shield` | Represents security |
| ECR | `package` | Represents container registry |
| IAM Role | `key` | Represents access/credentials |
| Service Discovery | `compass` | Represents discovery/navigation |
| AWS Credentials | `key-round` | Represents credentials/access |

## Using Official AWS Icons

To use **official AWS-branded icons**, you would need to:

1. **Create a Langflow Bundle** (requires frontend modifications):
   - Download AWS Architecture Icons from [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)
   - Convert SVGs to JSX components
   - Add to `src/frontend/src/icons/aws/` directory
   - Register in Langflow's bundle system

2. **Use AWS Icon Libraries** (alternative):
   - Libraries like `aws-icons` (npm) provide AWS icons via CDN
   - Would require custom icon component implementation
   - Not directly supported in Langflow's current component system

## Icon Resources

- **Lucide Icons**: https://lucide.dev/icons/
- **AWS Architecture Icons**: https://aws.amazon.com/architecture/icons/
- **AWS Icons Library (npm)**: https://www.npmjs.com/package/aws-icons

## Future Enhancement

For true AWS-branded icons, consider:
1. Creating a Langflow bundle with custom AWS icon components
2. Contributing AWS icon support to Langflow's core
3. Using icon URLs if Langflow adds support for external icon sources

## Current Status

✅ All components use proper Lucide icons (kebab-case format)
✅ Icons are visually distinct and recognizable
✅ Icons use best-matching Lucide icon names for each AWS service
⚠️ Icons are generic (not AWS-branded) but functional and well-matched

## Icon Format

All icons use **kebab-case** format (e.g., `network`, `server`, `container`) which is the standard format for Lucide icons in Langflow.
