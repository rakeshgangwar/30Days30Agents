import { Box, Container, Text, Flex, Link } from '@chakra-ui/react';

const Footer = () => {
  return (
    <Box as="footer" bg="app.footer" color="app.footerText" py={4}>
      <Container maxW="container.xl">
        <Flex direction={{ base: 'column', md: 'row' }} justifyContent="space-between" alignItems="center">
          <Text>&copy; {new Date().getFullYear()} Learning Coach Agent</Text>
          <Flex gap={4} mt={{ base: 2, md: 0 }}>
            <Link href="#" isExternal>
              Terms
            </Link>
            <Link href="#" isExternal>
              Privacy
            </Link>
            <Link href="#" isExternal>
              Help
            </Link>
          </Flex>
        </Flex>
      </Container>
    </Box>
  );
};

export default Footer;
